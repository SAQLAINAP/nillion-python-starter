from nada_dsl import *

def nada_main():
    # Define the parties
    party1 = Party(name="Party1")
    party2 = Party(name="Party2")
    
    # Define the inputs (SecretInteger inputs from respective parties)
    A = SecretInteger(Input(name="A", party=party1))
    B = SecretInteger(Input(name="B", party=party2))
    C = SecretInteger(Input(name="C", party=party1))
    D = SecretInteger(Input(name="D", party=party2))

    # Perform arithmetic operations
    left_expression = A * B + C
    right_expression = B * D
    
    # Comparison operation
    result = left_expression >= right_expression

    # Additional calculations
    sum_ab = A + B
    product_cd = C * D

    # Outputs
    outputs = [
        Output(left_expression, "Left_Expression_Result", party1),
        Output(right_expression, "Right_Expression_Result", party2),
        Output(result, "Comparison_Result", party1),
        Output(sum_ab, "Sum_AB", party1),
        Output(product_cd, "Product_CD", party2)
    ]

    return outputs
