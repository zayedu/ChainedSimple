# ChainedSimple

## Inspiration
After working at some of the largest Canadian banks, we identified a common problem: the traditional process of verifying financial statements for KYC compliance is slow, inefficient, and insecure. Common challenges include:
- Data tampering
- Lengthy verification processes
- Interbank trust barriers

These issues lead to a slow and tedious process for customer onboarding. Additionally, when financial statements are required for business activities such as credit scoring, verifying their accuracy can raise concerns, further slowing down transactions.

## What It Does
ChainedSimple is a solution that:
- Allows users to upload financial documents to the Blockchain.
- Enables access to these documents via a Wallet Address to share securely with others.
- Utilizes AI to analyze user data.

This approach ensures data integrity while keeping it more secure.

## How We Built It
- **Backend**: Built using Flask to handle API calls and support the application. We integrated the Verbwire API to mint NFTs and attach them to customer wallet addresses.
- **AI Integration**: The Cohere API was used for analyzing data.
- **Frontend**: Developed with standard HTML, CSS, and JavaScript to provide a user-friendly interface.

## Challenges We Ran Into
1. **Learning Curve**: None of us had prior experience with blockchain, and this was our first time implementing anything involving NFTs.
2. **Flask Challenges**: Understanding variable scope in Flask when passing data between pages or functions caused blockers during development.

## Accomplishments That We're Proud Of
We are extremely proud of:
- Successfully implementing the Verbwire API to mint NFTs with metadata and attach them to wallet addresses.
- Analyzing financial data using AI.
- Celebrating each milestone as we inched closer to completing our project.

## What We Learned
1. **Blockchain Fundamentals**: We gained a deep understanding of how the blockchain works and its benefits.
2. **Teamwork Lessons**: We realized that adding more hands to the wheel doesn’t always make the car drive faster—it just makes it harder to steer.

## What's Next for ChainedSimple
Our future plans include:
- Enhancing the UI for a smoother user experience.
- Adding workflows that allow users to share their NFT with others, such as through a QR code. This would enable users to share information like credit scores quickly and conveniently.

## Built With
- [Cohere](https://cohere.ai/)
- CSS
- [Figma](https://www.figma.com/)
- Flask
- HTML
- JavaScript
- Python
- [Verbwire](https://www.verbwire.com/)
