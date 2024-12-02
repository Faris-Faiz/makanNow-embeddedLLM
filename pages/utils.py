import streamlit as st
import googlemaps
import time
import requests
from jamaibase import JamAI
from jamaibase import protocol as p

def initialize_jamai(project_id, api_key):
    """Initialize JamAI client with proper error handling and user guidance"""
    if not project_id or not api_key:
        st.error("""
        ⚠️ JamAI credentials missing! Please provide both Project ID and API Key.
        
        Get your credentials from:
        - Project ID: Browse to any of your projects at cloud.jamaibase.com
        - API Key: Visit cloud.jamaibase.com/organization/secrets
        """)
        st.stop()
    
    return JamAI(project_id=project_id, token=api_key)

def initialize_tables(jamai):
    """Initialize JamAI tables for restaurant data and review processing"""
    try:
        # Create Knowledge Table for restaurant data
        jamai.table.create_knowledge_table(
            p.KnowledgeTableSchemaCreate(
                id="restaurants_data",
                cols=[],
                embedding_model="ellm/BAAI/bge-m3",
            )
        )
        
        # Create Action Table for review processing
        jamai.table.create_action_table(
            p.ActionTableSchemaCreate(
                id="review_processor",
                cols=[
                    p.ColumnSchemaCreate(id="review_text", dtype="str"),
                    p.ColumnSchemaCreate(
                        id="summary",
                        dtype="str",
                        gen_config=p.LLMGenConfig(
                            model="openai/gpt-4o-mini",
                            system_prompt="You are a restaurant review summarizer. Highlight key positive and negative points.",
                            prompt="Summarize these restaurant reviews:\n\n${review_text}",
                            temperature=0.3,
                            max_tokens=150,
                        ),
                    ),
                ],
            )
        )
    except RuntimeError as e:
        # Tables might already exist
        st.info("Tables already exist, proceeding with existing tables.")
    except Exception as e:
        st.error(f"""
        ❌ Error initializing JamAI tables. Please check:
        1. Your credentials are correct
        2. You have an active internet connection
        3. The JamAI service is available
        
        Error details: {str(e)}
        """)
        st.stop()

def get_photo_url(photo_reference, api_key, maxwidth=400):
    """
    Constructs the URL for fetching a place photo from Google Places API.
    
    Args:
        photo_reference (str): The photo reference from the Places API
        api_key (str): Your Google Maps API key
        maxwidth (int): Maximum width of the image (default 400px)
    
    Returns:
        str: The complete URL to fetch the photo
    """
    if not photo_reference:
        return None
        
    base_url = "https://maps.googleapis.com/maps/api/place/photo"
    photo_url = f"{base_url}?maxwidth={maxwidth}&photo_reference={photo_reference}&key={api_key}"
    return photo_url

def process_reviews(reviews, jamai):
    """Process restaurant reviews using JamAI"""
    if not reviews:
        return "No reviews available."
    
    try:
        # Take first 5 reviews and combine them
        review_texts = [review.get('text', '') for review in reviews[:5]]
        reviews_combined = "\n\n".join(review_texts)
        
        # Get review summary using non-streaming mode
        completion = jamai.table.add_table_rows(
            "action",
            p.RowAddRequest(
                table_id="review_processor",
                data=[{"review_text": reviews_combined}],
                stream=False,
            ),
        )
        
        if completion and completion.rows and len(completion.rows) > 0:
            return completion.rows[0].columns["summary"].text
        else:
            st.warning("⚠️ No summary generated. Please check JamAI console for table status.")
            return "Review processing unavailable."
            
    except Exception as e:
        st.warning(f"""
        ⚠️ Could not process reviews. Please check:
        1. JamAI console to ensure tables are created
        2. Your credentials are correct
        3. The model is available
        
        Error: {str(e)}
        """)
        return "Review processing unavailable."

def get_nearby_restaurants(google_api_key, location, radius, budget, preferences, exclude_no_price_info, jamai):
    """Get nearby restaurants with enhanced filtering and processing"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize Google Maps client
        status_text.info('Initializing Google Maps Client...')
        progress_bar.progress(10)
        gmaps = googlemaps.Client(key=google_api_key)
        
        # Get places nearby
        status_text.info('Searching for nearby restaurants...')
        progress_bar.progress(30)
        
        # Add preferences to keyword if provided
        keyword = "restaurant " + " ".join(preferences) if preferences else "restaurant"
        
        places_result = gmaps.places_nearby(
            location=location,
            radius=radius,
            keyword=keyword,
            type='restaurant'
        )
        
        restaurants = []
        processed_count = 0
        
        while places_result.get('results') and len(restaurants) < 3:
            status_text.info(f'Processing restaurant details...')
            progress_bar.progress(min(50 + (processed_count * 10), 90))
            
            for place in places_result['results']:
                # Get detailed place information
                place_details = gmaps.place(
                    place_id=place.get('place_id'),
                    fields=['price_level', 'opening_hours', 'name', 'vicinity', 'rating', 'reviews', 'photo', 'url']
                )
                
                result = place_details.get('result', {})
                price_level = result.get('price_level', None)
                
                # Filter based on price level and budget
                if price_level is not None:
                    estimated_cost = price_level * 25  # Rough estimate: $25 per price level
                    if estimated_cost > budget:
                        continue
                
                # Skip if no price info and exclude_no_price_info is True
                if exclude_no_price_info and price_level is None:
                    continue
                
                # Get photo URL
                photos = result.get('photos', [])
                photo_url = None
                if photos:
                    try:
                        photo_url = get_photo_url(photos[0]['photo_reference'], google_api_key)
                    except (KeyError, IndexError) as e:
                        print(f"Error processing photo: {e}")
                
                # Process reviews
                reviews = result.get('reviews', [])
                review_summary = process_reviews(reviews, jamai)
                
                restaurant = {
                    'name': result.get('name', 'N/A'),
                    'address': result.get('vicinity', 'N/A'),
                    'price_level': price_level,
                    'rating': result.get('rating', 'N/A'),
                    'photo_url': photo_url,
                    'review_summary': review_summary,
                    'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                    'url': result.get('url', 'N/A')
                }
                
                restaurants.append(restaurant)
                processed_count += 1
                
                if len(restaurants) >= 3:
                    break
            
            # Break if we have enough restaurants
            if len(restaurants) >= 3:
                break
            
            # Get next page if available
            if 'next_page_token' in places_result:
                time.sleep(2)  # Wait for next page token to be valid
                places_result = gmaps.places_nearby(
                    location=location,
                    radius=radius,
                    keyword=keyword,
                    type='restaurant',
                    page_token=places_result['next_page_token']
                )
            else:
                break
        
        # Final progress
        status_text.success(f'Found {len(restaurants)} restaurants!')
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clear status and progress
        status_text.empty()
        progress_bar.empty()
        
        return restaurants
    
    except Exception as e:
        # Clear progress indicators
        status_text.empty()
        progress_bar.empty()
        raise
