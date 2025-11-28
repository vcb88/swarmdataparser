
import sqlite3
import os

DATABASE_NAME = 'foursquare_data.db'

def verify_data():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    print("--- Verifying Checkins Table ---")
    cursor.execute("SELECT COUNT(*) FROM checkins")
    checkins_count = cursor.fetchone()[0]
    print(f"Total checkins in database: {checkins_count}")

    print("\n--- Sample Checkins (first 5) ---")
    cursor.execute("SELECT * FROM checkins LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Photos Table ---")
    cursor.execute("SELECT COUNT(*) FROM photos")
    photos_count = cursor.fetchone()[0]
    print(f"Total photos in database: {photos_count}")

    print("\n--- Sample Photos (first 5) ---")
    cursor.execute("SELECT * FROM photos LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    
    print("\n--- Photos without a linked checkin (first 5) ---")
    cursor.execute("SELECT p.* FROM photos p LEFT JOIN checkins c ON p.checkinId = c.id WHERE c.id IS NULL LIMIT 5")
    photos_without_checkin = cursor.fetchall()
    if photos_without_checkin:
        print("Found photos not linked to any checkin:")
        for row in photos_without_checkin:
            print(row)
    else:
        print("All photos seem to be linked to a checkin.")

    print("\n--- Verifying Users Table ---")
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    print(f"Total users in database: {users_count}")
    print("\n--- Sample Users (first 5) ---")
    cursor.execute("SELECT * FROM users LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Friends Table ---")
    cursor.execute("SELECT COUNT(*) FROM friends")
    friends_count = cursor.fetchone()[0]
    print(f"Total friends in database: {friends_count}")
    print("\n--- Sample Friends (first 5) ---")
    cursor.execute("SELECT * FROM friends LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Visits Table ---")
    cursor.execute("SELECT COUNT(*) FROM visits")
    visits_count = cursor.fetchone()[0]
    print(f"Total visits in database: {visits_count}")
    print("\n--- Sample Visits (random 10) ---")
    cursor.execute("SELECT * FROM visits ORDER BY RANDOM() LIMIT 10")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Unconfirmed Visits Table ---")
    cursor.execute("SELECT COUNT(*) FROM unconfirmed_visits")
    unconfirmed_visits_count = cursor.fetchone()[0]
    print(f"Total unconfirmed visits in database: {unconfirmed_visits_count}")
    print("\n--- Sample Unconfirmed Visits (random 10) ---")
    cursor.execute("SELECT * FROM unconfirmed_visits ORDER BY RANDOM() LIMIT 10")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Tips Table ---")
    cursor.execute("SELECT COUNT(*) FROM tips")
    tips_count = cursor.fetchone()[0]
    print(f"Total tips in database: {tips_count}")
    print("\n--- Sample Tips (first 5) ---")
    cursor.execute("SELECT * FROM tips LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Comments Table ---")
    cursor.execute("SELECT COUNT(*) FROM comments")
    comments_count = cursor.fetchone()[0]
    print(f"Total comments in database: {comments_count}")
    print("\n--- Sample Comments (first 5) ---")
    cursor.execute("SELECT * FROM comments LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Venue Ratings Table ---")
    cursor.execute("SELECT COUNT(*) FROM venue_ratings")
    venue_ratings_count = cursor.fetchone()[0]
    print(f"Total venue ratings in database: {venue_ratings_count}")
    print("\n--- Sample Venue Ratings (first 5) ---")
    cursor.execute("SELECT * FROM venue_ratings LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    
    print("\n--- Verifying Expertise Table ---")
    cursor.execute("SELECT COUNT(*) FROM expertise")
    expertise_count = cursor.fetchone()[0]
    print(f"Total expertise entries in database: {expertise_count}")
    print("\n--- Sample Expertise (first 5) ---")
    cursor.execute("SELECT * FROM expertise LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Plans Table ---")
    cursor.execute("SELECT COUNT(*) FROM plans")
    plans_count = cursor.fetchone()[0]
    print(f"Total plans in database: {plans_count}")
    print("\n--- Sample Plans (first 5) ---")
    cursor.execute("SELECT * FROM plans LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Shares Table ---")
    cursor.execute("SELECT COUNT(*) FROM shares")
    shares_count = cursor.fetchone()[0]
    print(f"Total shares in database: {shares_count}")
    print("\n--- Sample Shares (first 5) ---")
    cursor.execute("SELECT * FROM shares LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Verifying Venues Table ---")
    cursor.execute("SELECT COUNT(*) FROM venues")
    venues_count = cursor.fetchone()[0]
    print(f"Total venues in database: {venues_count}")
    print("\n--- Sample Venues (random 20) ---")
    cursor.execute("SELECT * FROM venues ORDER BY RANDOM() LIMIT 20")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == '__main__':
    verify_data()
