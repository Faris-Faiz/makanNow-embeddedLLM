import streamlit as st
import geocoder
from utils import (
    initialize_jamai,
    initialize_tables,
    get_nearby_restaurants
)

st.set_page_config(page_title="Restaurant Finder", page_icon="🍽️", layout="wide")

def main():
    st.title('🍽️ Smart Restaurant Finder')
    
    # Sidebar for inputs
    st.sidebar.header('API Credentials')
    
    # Google Maps API Key input with help text
    st.sidebar.markdown("""
    ### Google Maps API Key
    Get your API key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
    1. Create a new project
    2. Enable Places API
    3. Create credentials (API key)
    """)
    google_api_key = st.sidebar.text_input('Enter Google Maps API Key', type='password')
    
    # JamAI credentials with help text
    st.sidebar.markdown("""
    ### JamAI Credentials
    Get your credentials from [JamAI Cloud](https://cloud.jamaibase.com)
    1. Project ID: Browse to any project page
    2. API Key: Visit organization secrets page
    """)
    jamai_project_id = st.sidebar.text_input('Enter JamAI Project ID', type='password')
    jamai_api_key = st.sidebar.text_input('Enter JamAI API Key', type='password')
    
    st.sidebar.markdown("---")
    st.sidebar.header('Search Parameters')
    
    # Budget input
    budget = st.sidebar.number_input('Your Budget (USD)', min_value=10, max_value=500, value=50, step=10,
                                   help='Maximum amount you want to spend per person')
    
    # Radius slider
    radius = st.sidebar.slider('Search Radius (meters)', 500, 10000, 2000,
                             help='Adjust the search area around your location')
    
    # Preferences multi-select
    preferences = st.sidebar.multiselect(
        'Food Preferences',
        ['Halal', 'Vegetarian', 'Vegan', 'Seafood', 'Fast Food', 'Fine Dining'],
        help='Select your food preferences'
    )
    
    # Exclude restaurants without price info
    exclude_no_price = st.sidebar.checkbox(
        'Exclude Restaurants without Price Info',
        value=True,
        help='If checked, restaurants with no price information will be filtered out'
    )
    
    # Find restaurants button
    if st.sidebar.button('Find Restaurants'):
        # Validate all API credentials
        if not google_api_key:
            st.error('🚨 Please enter a Google Maps API Key')
            return
        if not jamai_project_id or not jamai_api_key:
            st.error('🚨 Please enter both JamAI Project ID and API Key')
            return
        
        try:
            # Initialize JamAI client
            jamai = initialize_jamai(jamai_project_id, jamai_api_key)
            
            # Initialize JamAI tables
            initialize_tables(jamai)
            
            # Use spinner for location detection
            with st.spinner('Detecting your current location...'):
                # Get current location
                g = geocoder.ip('me')
                location = (g.latlng[0], g.latlng[1])
                
                # Display current location
                st.info(f"📍 Searching near: {g.city}, {g.state}, {g.country}")
                
                # Find restaurants
                restaurants = get_nearby_restaurants(
                    google_api_key,
                    location,
                    radius,
                    budget,
                    preferences,
                    exclude_no_price,
                    jamai
                )
                
                # Display results
                if restaurants:
                    st.header('🍴 Recommended Restaurants')
                    
                    # Create three columns for restaurant cards
                    cols = st.columns(3)
                    
                    for idx, restaurant in enumerate(restaurants):
                        with cols[idx]:
                            st.subheader(restaurant['name'])
                            
                            # Display restaurant photo
                            if restaurant['photo_url']:
                                st.image(restaurant['photo_url'], use_container_width=True)
                            
                            st.write(f"**Address:** {restaurant['address']}")
                            st.write(f"**Price Level:** {'$' * restaurant['price_level'] if restaurant['price_level'] else 'N/A'}")
                            st.write(f"**Rating:** {'⭐' * int(restaurant['rating']) if restaurant['rating'] != 'N/A' else 'N/A'}")
                            st.markdown(f"**[View on Google Maps]({restaurant['url']})**")
                            
                            # Display opening hours in an expander
                            with st.expander("Opening Hours"):
                                if restaurant['opening_hours']:
                                    for hours in restaurant['opening_hours']:
                                        st.write(hours)
                                else:
                                    st.write("Opening hours not available")
                            
                            # Display review summary in an expander
                            with st.expander("Review Summary"):
                                st.write(restaurant['review_summary'])
                else:
                    st.warning('🔍 No restaurants found matching your criteria. Try adjusting your preferences or increasing the radius.')
        
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
