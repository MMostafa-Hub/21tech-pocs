import math

def estimate_months(principal, annual_interest_rate, max_monthly_payment):
    """
    Estimate the number of months needed to repay a loan with a given max monthly payment
    under a reducing balance interest model (approximate).
    """
    r = annual_interest_rate / 100
    months = 1

    while months < 1000:  # limit to avoid infinite loops
        total_interest = (principal * r * (months + 1)) / 24
        total_payment = principal + total_interest
        monthly_installment = total_payment / months

        if monthly_installment <= max_monthly_payment:
            return {
                "months": months,
                "monthly_installment": round(monthly_installment, 2),
                "total_interest": round(total_interest, 2),
                "total_repayment": round(total_payment, 2)
            }

        months += 1

    return None  # If not found within 1000 months

# Example usage
if __name__ == "__main__":
    principal = float(input("Enter loan amount (EGP): "))
    annual_interest_rate = float(input("Enter annual interest rate (%): "))
    max_monthly_payment = float(input("Enter max affordable monthly payment (EGP): "))

    result = estimate_months(principal, annual_interest_rate, max_monthly_payment)

    if result:
        print("\n--- Estimation Result ---")
        print(f"Estimated Months to Repay: {result['months']} months")
        print(f"Monthly Installment: {result['monthly_installment']} EGP")
        print(f"Total Interest: {result['total_interest']} EGP")
        print(f"Total Repayment: {result['total_repayment']} EGP")
    else:
        print("Couldn't find a feasible repayment plan under the given constraints.")
