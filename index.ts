interface ProcessablePayment {
    process(amount: number): boolean;
}

abstract class PaymentGateway implements ProcessablePayment {
    protected environment: string;

    constructor(p_environment: string) {
        this.environment = p_environment
    }

    logTransaction(amount: number): void {
        console.log(`[${this.environment.toUpperCase()}] Processing $${amount}...`)
    }

    abstract process(amount: number): boolean;
}

class CreditCardGateway extends PaymentGateway {
    private cardNumber: string;

    constructor(p_cardNumber: string, p_environment: string) {
        super(p_environment)

        this.cardNumber = p_cardNumber
    }

    process(amount: number): boolean {
        this.logTransaction(amount)
        console.log(`Card Number Last Digits ${this.cardNumber.slice(-4)}`)

        return true
    }
}

class PayPalGateway extends PaymentGateway {
    private userEmail: string;

    constructor(p_userEmail: string, p_environment: string) {
        super(p_environment)

        this.userEmail = p_userEmail
    }

    process(amount: number): boolean {
        this.logTransaction(amount)
        console.log(`Process amount associated with ${this.userEmail}`)

        return true
    }
}

const cardPayment: ProcessablePayment = new CreditCardGateway("4111222233334444", "production");
cardPayment.process(99.99);

const paypalPayment: ProcessablePayment = new PayPalGateway("dev@user.com", "sandbox");
paypalPayment.process(15.50);
