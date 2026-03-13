📖 Overview

The end-to-end credit scoring system designed to process customer data, calculate credit scores using a machine learning model, and expose this functionality via a scalable web API. It is structured into two main components:

data_pipeline: Responsible for data ingestion, preprocessing, feature engineering, and training/managing the credit scoring machine learning model. This component ensures the model is up-to-date and robust.

web_service: Provides a RESTful API that allows external applications to submit customer information and retrieve real-time credit scores. It integrates with the trained model from the data pipeline and handles business logic related to scoring requests.
This architecture enables a clear separation of concerns, allowing for independent development, scaling, and deployment of the data science and application logic.

✨ Features

🎯 Automated Credit Score Calculation: Utilizes a machine learning model to compute credit scores based on input data.

⚙️ Data Preprocessing & Feature Engineering: Robust data pipeline for transforming raw data into features suitable for the ML model.

🌐 Scalable RESTful API: Provides endpoints for seamless integration with client applications to request credit scores.

🧠 Machine Learning Model Management: Infrastructure to train, evaluate, and potentially update the credit scoring model.

🔒 Secure API Endpoints: Authentication and authorization mechanisms for API access.

🛠️ Modular Architecture: Separate components for data handling and web service, promoting maintainability and extensibility
