import asyncio
import os
from dotenv import load_dotenv
from py_nillion_client import NodeKey, UserKey, NadaValues, SecretInteger, Party, Output, create_nillion_client, create_payments_config, LedgerClient, LocalWallet
import py_nillion_client as nillion

# Load environment variables
home = os.getenv("HOME")
load_dotenv(f"{home}/.config/nillion/nillion-devnet.env")

async def main():
    # 1. Initialize NillionClient against nillion-devnet
    # Get cluster_id, grpc_endpoint, & chain_id from the .env file
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    grpc_endpoint = os.getenv("NILLION_NILCHAIN_GRPC")
    chain_id = os.getenv("NILLION_NILCHAIN_CHAIN_ID")

    # Create user and node keys
    seed = "my_seed"  # Replace with your actual seed phrase
    userkey = UserKey.from_seed(seed)
    nodekey = NodeKey.from_seed(seed)

    # Create Nillion Client for user
    client = create_nillion_client(userkey, nodekey)

    # Get party_id and user_id
    party_id = client.party_id
    user_id = client.user_id

    # 2. Pay for and store the program (markscard program)
    # Set the program name and path to the compiled program
    program_name = "markscard"
    program_mir_path = f"../nada_quickstart_programs/target/{program_name}.nada.bin"

    # Create payments config, client and wallet
    payments_config = create_payments_config(chain_id, grpc_endpoint)
    payments_client = LedgerClient(payments_config)
    payments_wallet = LocalWallet(
        nillion.PrivateKey(bytes.fromhex(os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0"))),
        prefix="nillion",
    )

    # Pay to store the program and obtain a receipt of the payment
    receipt_store_program = await nillion.get_quote_and_pay(
        client,
        nillion.Operation.store_program(program_mir_path),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    # Store the program
    action_id = await client.store_program(
        cluster_id, program_name, program_mir_path, receipt_store_program
    )

    # Create a variable for the program_id
    program_id = f"{user_id}/{program_name}"
    print("Stored program. action_id:", action_id)
    print("Stored program_id:", program_id)

    # 3. Define input values (marks for different subjects)
    marks_values = NadaValues({
        "Math_Marks": SecretInteger(85),
        "Science_Marks": SecretInteger(75),
        "English_Marks": SecretInteger(80),
        "History_Marks": SecretInteger(90),
        "Geography_Marks": SecretInteger(88)
    })

    # Pay for and store the input values
    receipt_store_values = await nillion.get_quote_and_pay(
        client,
        nillion.Operation.store_values(marks_values, ttl_days=5),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    # Store the input values
    values_store_id = await client.store_values(
        cluster_id, marks_values, nillion.Permissions.default_for_user(client.user_id), receipt_store_values
    )
    print(f"Stored input values. Store ID: {values_store_id}")

    # 4. Create compute bindings, add input and output parties, compute with the stored values
    compute_bindings = nillion.ProgramBindings(program_id)
    compute_bindings.add_input_party("Party1", party_id)
    compute_bindings.add_output_party("Party1", party_id)

    # Define computation time secrets (if any)
    computation_time_secrets = NadaValues({})

    # Pay for the compute
    receipt_compute = await nillion.get_quote_and_pay(
        client,
        nillion.Operation.compute(program_id, computation_time_secrets),
        payments_wallet,
        payments_client,
        cluster_id,
    )

    # Compute with the stored values
    compute_id = await client.compute(
        cluster_id, compute_bindings, [values_store_id], computation_time_secrets, receipt_compute
    )

    print(f"Compute sent to network. Compute ID: {compute_id}")

    # 5. Retrieve and print the result
    while True:
        compute_event = await client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(f"✅  Compute complete for compute_id {compute_event.uuid}")
            print(f"🖥️  The result is {compute_event.result.value}")
            return compute_event.result.value

if __name__ == "__main__":
    asyncio.run(main())
