# MakanNow - Smart Restaurant Finder 🍽️

A sophisticated restaurant discovery application that helps users find nearby restaurants based on their preferences, budget, and location. The application uses AI-powered review summarization and provides detailed information about restaurants including photos, ratings, and opening hours.

## Features 🌟

- **Location-Based Search**: Automatically detects user's location to find nearby restaurants
- **Customizable Search Parameters**:
  - Adjustable search radius (500m - 10km)
  - Budget preferences
  - Food preferences (Halal, Vegetarian, Vegan, Seafood, etc.)
- **Smart Filtering**:
  - Price-based filtering
  - Option to exclude restaurants without price information
- **Rich Restaurant Information**:
  - Restaurant photos
  - Price levels
  - Ratings
  - Opening hours
  - Direct Google Maps links
- **AI-Powered Review Summaries**: Utilizes JamAI to generate concise summaries of restaurant reviews

## Technologies Used 🛠️

- **Frontend**: Streamlit
- **APIs**:
  - Google Maps Places API
  - Geocoding
- **AI/ML**:
  - JamAI for review processing
  - BAAI/bge-m3 embedding model
  - Llama3.1 for review summarization

## Prerequisites 📋

- Python 3.6+
- Google Maps API Key
- JamAI Account with API credentials

## Installation 🔧

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/makanNow-embeddedLLM.git
   cd makanNow-embeddedLLM
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with your API credentials:
   ```env
   JAMAI_PROJECT_ID=your_project_id
   JAMAI_API_KEY=your_api_key
   ```

## Usage 📱

1. Start the application:
   ```bash
   streamlit run pages/1_Nearby_Restaurants.py
   ```

2. In the sidebar:
   - Enter your Google Maps API Key
   - Set your budget
   - Adjust the search radius
   - Select food preferences
   - Choose whether to exclude restaurants without price information

3. Click "Find Restaurants" to see recommendations

## API Setup Guide 🔑

### Google Maps API
1. Visit [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project
3. Enable the Places API
4. Create credentials (API key)
5. Use the API key in the application

### JamAI Setup
1. Visit [JamAI Cloud](https://cloud.jamaibase.com)
2. Create an account/login
3. Get your Project ID from any project page
4. Obtain API Key from organization secrets page
5. Add credentials to your `.env` file

## Dependencies 📦

```
streamlit
pandas
plotly
numpy
googlemaps
geocoder
jamaibase
requests
python-dotenv
```

## Project Structure 📁

```
makanNow-embeddedLLM/
├── pages/
│   ├── 1_Nearby_Restaurants.py   # Main application file
│   └── utils.py                  # Utility functions and API handlers
├── requirements.txt              # Project dependencies
└── README.md                    # Project documentation
```

## Features in Detail 🔍

### Restaurant Information
- Name and address
- Price level indicator
- Rating with star visualization
- Opening hours
- Direct link to Google Maps
- Restaurant photos (when available)

### AI-Powered Review Processing
- Aggregates multiple reviews
- Generates concise summaries
- Highlights key positive and negative points
- Uses advanced language models for accurate summarization

## Error Handling 🛡️

The application includes robust error handling for:
- API connection issues
- Location detection failures
- Missing credentials
- Review processing errors
- Data retrieval problems

## Privacy and Security 🔒

- API keys are securely stored in `.env` file
- User location data is used only for search purposes
- No personal data is stored or transmitted
