import tweepy
import csv
import time

# Authentication
bearer_token = "AAAAAAAAAAAAAAAAAAAAAJomzwEAAAAAAkEy3H4ARbHGjPazNbUNCBvPf3k%3Dybg4fK4vSKeknqG9xU8ua0UED63q9TjPOAnJOBAoZCFf64RfXJ"
client = tweepy.Client(bearer_token=bearer_token)

political_accounts = [
    "@INCIndia"
]

filename = "recent_political_tweets.csv"

with open(filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Account", "Date", "Tweet", "Source", "Likes", "Retweets", "Replies", "Quotes"])

    for account in political_accounts:
        print(f"Fetching up to 100 recent tweets from @{account}")

        try:
            user = client.get_user(username=account)
            response = client.get_users_tweets(
                id=user.data.id,
                max_results=100,
                tweet_fields=["created_at", "public_metrics", "source"]
            )

            if not response.data:
                print(f"No recent tweets found for @{account}.")
                continue

            for tweet in response.data:
                metrics = tweet.public_metrics
                writer.writerow([
                    account,
                    tweet.created_at,
                    tweet.text.replace("\n", " "),
                    tweet.source,
                    metrics['like_count'],
                    metrics['retweet_count'],
                    metrics['reply_count'],
                    metrics['quote_count']
                ])

            print(f"✅ Fetched tweets for @{account}")

            # Avoid hitting rate limit
            time.sleep(20)

        except tweepy.TooManyRequests:
            print(f"⚠ Rate limit hit for @{account}. Waiting 15 minutes...")
            time.sleep(15 * 60)

print(f"✅ All recent data saved to '{filename}'")