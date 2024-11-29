import requests
import tweepy
import secrets_original
import time
import os
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont

# Authenticate with Twitter API v1.1 for media upload
auth = tweepy.OAuthHandler(secrets_original.consumer_key, secrets_original.consumer_secret)
auth.set_access_token(secrets_original.access_token, secrets_original.access_token_secret)
api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
print("Authenticated with Twitter API v1.1 for media upload.")

# Authenticate with Twitter API v2 for posting tweets
client_v2 = tweepy.Client(
    bearer_token=secrets_original.bearer_token,
    consumer_key=secrets_original.consumer_key,
    consumer_secret=secrets_original.consumer_secret,
    access_token=secrets_original.access_token,
    access_token_secret=secrets_original.access_token_secret
)
print("Authenticated with Twitter API v2 for tweet posting.")

# Paths to the extracted frames (located in the same folder as the script)
frame_paths = [f"frame_{i}.png" for i in range(4)]


# Fetch current Bitcoin price
def get_bitcoin_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['bitcoin']['usd']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bitcoin price: {e}")
        return None


# Fetch historical Bitcoin price for a given interval
def get_historical_bitcoin_price(interval_seconds):
    try:
        timestamp = int(time.time()) - interval_seconds
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={timestamp}&to={time.time()}"
        response = requests.get(url)
        response.raise_for_status()
        prices = response.json().get("prices", [])
        return prices[0][1] if prices else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical Bitcoin price: {e}")
        return None


# Get Google trend data
def get_trend_data():
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        kw_list = ["bitcoin"]
        pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')
        interest_over_time_df = pytrends.interest_over_time()

        if interest_over_time_df.empty:
            print('No data retrieved')
            return None

        latest_data = interest_over_time_df.iloc[-1]
        trend_value_today = latest_data['bitcoin']
        return trend_value_today
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Fetch current block height
def get_block_height():
    try:
        url = "https://mempool.space/api/blocks/tip/height"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching block height: {e}")
        return None


# Fetch USD price
def get_usd_price():
    try:
        url = "https://mempool.space/api/v1/prices"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching USD price: {e}")
        return None


# Fetch recommended mempool fees
def get_recommended_fees():
    try:
        url = "https://mempool.space/api/v1/fees/recommended"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching mempool fees: {e}")
        return None


# Create roller coaster GIF
def generate_roller_coaster_gif():
    intervals = {
        "1 Hour": 3600,
        "1 Week": 7 * 24 * 3600,
        "1 Month": 30 * 24 * 3600,
        "6 Months": 180 * 24 * 3600
    }

    price_now = get_bitcoin_price()
    if price_now is None:
        print("Error: Unable to fetch current Bitcoin price.")
        return None

    price_changes = {}
    for label, seconds in intervals.items():
        historical_price = get_historical_bitcoin_price(seconds)
        if historical_price:
            percentage_change = ((price_now - historical_price) / historical_price) * 100
            price_changes[label] = percentage_change
        else:
            price_changes[label] = None

    angle = max(-90, min(90, (price_changes["1 Week"] / 10) * 90)) if price_changes["1 Week"] is not None else 0

    rotated_frames = []
    for frame_path in frame_paths:
        if not os.path.exists(frame_path):
            print(f"Error: Frame file {frame_path} not found.")
            return None

        img = Image.open(frame_path)
        rotated_img = img.rotate(angle, resample=Image.BICUBIC, expand=True)

        draw = ImageDraw.Draw(rotated_img)
        font_path = "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"

        try:
            font = ImageFont.truetype(font_path, 70)
        except OSError:
            print("Warning: Arial font not found. Using default PIL font.")
            font = ImageFont.load_default()

        y_offset = 10
        draw.text((10, y_offset), f"BTC: ${price_now:.2f}", fill="white", font=font)
        y_offset += 70

        for label, change in price_changes.items():
            color = "green" if change > 0 else "red"
            text = f"{label}: {change:+.2f}%" if change is not None else f"{label}: Data Unavailable"
            draw.text((10, y_offset), text, fill=color, font=font)
            y_offset += 70

        rotated_frames.append(rotated_img)

    output_gif_path = "bitcoin_roller_coaster.gif"
    rotated_frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=rotated_frames[1:],
        duration=100,
        loop=0
    )

    print(f"Dynamic roller coaster GIF created! Saved at {output_gif_path}")
    return output_gif_path


# Post tweet with GIF using v1 for media upload and v2 for posting
def post_tweet_with_gif_combined(gif_path, tweet_text):
    try:
        # Step 1: Upload media using API v1.1
        print(f"Uploading GIF: {gif_path}")
        media = api_v1.media_upload(gif_path)
        print(f"Media uploaded successfully. Media ID: {media.media_id}")

        # Step 2: Post tweet using API v2
        response = client_v2.create_tweet(text=tweet_text, media_ids=[media.media_id])
        print("Tweet posted successfully.")
        print("Tweet ID:", response.data["id"])
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Main function to check and notify users
def check_and_notify_users():
    recommended_fees = get_recommended_fees()
    usd_price = get_usd_price()
    block_height = get_block_height()
    trend_data = get_trend_data()
    gif_path = generate_roller_coaster_gif()

    if None in (recommended_fees, usd_price, block_height, trend_data, gif_path):
        print("Missing data or GIF. Tweet cannot be posted.")
        return

    fastest_fee = recommended_fees['fastestFee']
    simple_fee = fastest_fee * 250
    price = usd_price['USD']
    usd_fee = round(simple_fee * price / 100000000, 2)
    block_height_formatted = "{:,}".format(block_height)

    tweet_text = (
        f"The fastest #Bitcoin fee is currently {fastest_fee} sat/vB. "
        f"A simple transaction could have a fee of approximately {simple_fee:,} Satoshis "
        f"(${usd_fee:.2f}). 🔍 Bitcoin price: ${price:,.2f}. "
        f"Google trend: {trend_data}/100. Block height: {block_height_formatted}."
    )

    post_tweet_with_gif_combined(gif_path, tweet_text)


# Script entry point
if __name__ == "__main__":
    try:
        while True:
            check_and_notify_users()
            time.sleep(21600)  # 6 hours
    except KeyboardInterrupt:
        print("Script terminated by user.")
