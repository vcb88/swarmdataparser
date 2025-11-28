
import sqlite3
import json
import os
import re

DATABASE_NAME = 'foursquare_data.db'
PIX_DIR = 'pix' # Directory where images are stored

def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create checkins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id TEXT PRIMARY KEY,
            createdAt TEXT,
            venueId TEXT,
            shout TEXT,
            timeZone TEXT,
            FOREIGN KEY (venueId) REFERENCES venues(id)
        )
    ''')

    # Create photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id TEXT PRIMARY KEY,
            checkinId TEXT,
            createdAt TEXT,
            fullUrl TEXT,
            localPath TEXT,
            width INTEGER,
            height INTEGER,
            FOREIGN KEY (checkinId) REFERENCES checkins(id)
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            firstName TEXT,
            lastName TEXT,
            email TEXT,
            gender TEXT,
            homeCity TEXT,
            bio TEXT,
            phone TEXT,
            verifiedPhone BOOLEAN,
            verifiedEmail BOOLEAN,
            facebook TEXT,
            photoPrefix TEXT,
            photoSuffix TEXT,
            birthday INTEGER,
            displayName TEXT,
            tipsCount INTEGER,
            listsCount INTEGER
        )
    ''')

    # Create friends table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            userId TEXT,
            friendId TEXT,
            friendFirstName TEXT,
            friendLastName TEXT,
            friendCanonicalUrl TEXT,
            PRIMARY KEY (userId, friendId),
            FOREIGN KEY (userId) REFERENCES users(id)
        )
    ''')

    # Create visits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id TEXT PRIMARY KEY,
            userId TEXT,
            timeArrived TEXT,
            timeDeparted TEXT,
            os TEXT,
            osVersion TEXT,
            deviceModel TEXT,
            isTraveling BOOLEAN,
            latitude REAL,
            longitude REAL,
            city TEXT,
            state TEXT,
            countryCode TEXT,
            locationType TEXT,
            FOREIGN KEY (userId) REFERENCES users(id)
        )
    ''')

    # Create unconfirmed_visits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unconfirmed_visits (
            id TEXT PRIMARY KEY,
            startTime TEXT,
            endTime TEXT,
            venueId TEXT,
            lat REAL,
            lng REAL,
            FOREIGN KEY (venueId) REFERENCES venues(id)
        )
    ''')

    # Create tips table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tips (
            id TEXT PRIMARY KEY,
            createdAt TEXT,
            text TEXT,
            type TEXT,
            canonicalUrl TEXT,
            viewCount INTEGER,
            agreeCount INTEGER,
            disagreeCount INTEGER,
            userId TEXT,
            venueId TEXT,
            FOREIGN KEY (userId) REFERENCES users(id),
            FOREIGN KEY (venueId) REFERENCES venues(id)
        )
    ''')

    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId TEXT,
            time TEXT,
            comment TEXT,
            FOREIGN KEY (userId) REFERENCES users(id)
        )
    ''')

    # Create venue_ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venue_ratings (
            id TEXT PRIMARY KEY,
            name TEXT,
            url TEXT
        )
    ''')

    # Create expertise table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expertise (
            id TEXT PRIMARY KEY,
            type TEXT,
            timestamp TEXT,
            lastModified TEXT
        )
    ''')

    # Create plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id TEXT PRIMARY KEY,
            userId TEXT,
            createdAt TEXT,
            modifiedTime TEXT,
            isBroadcast BOOLEAN,
            type TEXT,
            FOREIGN KEY (userId) REFERENCES users(id)
        )
    ''')

    # Create shares table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shares (
            id TEXT PRIMARY KEY,
            sharedAt TEXT,
            state TEXT,
            type TEXT
        )
    ''')

    # Create venues table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            id TEXT PRIMARY KEY,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            url TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' and tables 'checkins', 'photos', 'users', 'friends', 'visits', 'unconfirmed_visits', 'tips', 'comments', 'venue_ratings', 'expertise', 'plans', 'shares', 'venues' set up successfully.")


def import_venues_data():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    total_venues_imported = 0

    # From checkins
    checkin_files = [f for f in os.listdir('.') if f.startswith('checkins') and f.endswith('.json')]
    print(f"DEBUG: Found checkin files: {checkin_files}")
    for filename in checkin_files:
        print(f"DEBUG: Processing checkins file for venues: {filename}")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data.get('items', []):
                venue = item.get('venue', {})
                venue_id = venue.get('id')
                venue_name = venue.get('name')
                location = venue.get('location', {})
                venue_address = location.get('address')
                venue_lat = location.get('lat')
                venue_lng = location.get('lng')
                
                if venue_id:
                    print(f"DEBUG: Found venue_id: {venue_id}, name: {venue_name}, address: {venue_address}, lat: {venue_lat}, lng: {venue_lng}")
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO venues (id, name, address, lat, lng)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (venue_id, venue_name, venue_address, venue_lat, venue_lng))
                        if cursor.rowcount > 0:
                            total_venues_imported += 1
                            print(f"DEBUG: Inserted venue {venue_id}. Total imported: {total_venues_imported}")
                        else:
                            print(f"DEBUG: Skipped existing venue {venue_id}.")
                    except sqlite3.Error as e:
                        print(f"Error importing venue {venue_id} from checkins: {e}")

    # From unconfirmed_visits
    try:
        with open('unconfirmed_visits.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"DEBUG: Processing unconfirmed_visits.json for venues.")
            for item in data.get('items', []):
                venue_id = item.get('venueId')
                venue = item.get('venue', {})
                venue_name = venue.get('name')
                venue_url = venue.get('url')
                lat = item.get('lat')
                lng = item.get('lng')

                if venue_id:
                    print(f"DEBUG: Found venue_id (unconfirmed): {venue_id}, name: {venue_name}, lat: {lat}, lng: {lng}, url: {venue_url}")
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO venues (id, name, lat, lng, url)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (venue_id, venue_name, lat, lng, venue_url))
                        if cursor.rowcount > 0:
                            total_venues_imported += 1
                            print(f"DEBUG: Inserted venue (unconfirmed) {venue_id}. Total imported: {total_venues_imported}")
                        else: # Update existing entry if new info is available
                            cursor.execute('''
                                UPDATE venues SET name = COALESCE(?, name), lat = COALESCE(?, lat), lng = COALESCE(?, lng), url = COALESCE(?, url)
                                WHERE id = ? AND (name IS NULL OR lat IS NULL OR lng IS NULL OR url IS NULL)
                            ''', (venue_name, lat, lng, venue_url, venue_id))
                            if cursor.rowcount > 0:
                                print(f"DEBUG: Updated venue (unconfirmed) {venue_id}. Total imported: {total_venues_imported}")
                            else:
                                print(f"DEBUG: No update needed for venue (unconfirmed) {venue_id}.")
                    except sqlite3.Error as e:
                        print(f"Error importing venue {venue_id} from unconfirmed_visits: {e}")
    except FileNotFoundError:
        print("unconfirmed_visits.json not found. Skipping.")
    except Exception as e:
        print(f"Error processing unconfirmed_visits.json for venues: {e}")

    # From tips
    try:
        with open('tips.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"DEBUG: Processing tips.json for venues.")
            for item in data.get('items', []):
                venue = item.get('venue', {})
                venue_id = venue.get('id')
                venue_name = venue.get('name')

                if venue_id:
                    print(f"DEBUG: Found venue_id (tips): {venue_id}, name: {venue_name}")
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO venues (id, name)
                            VALUES (?, ?)
                        ''', (venue_id, venue_name))
                        if cursor.rowcount > 0:
                            total_venues_imported += 1
                            print(f"DEBUG: Inserted venue (tips) {venue_id}. Total imported: {total_venues_imported}")
                        else: # Update existing entry if new info is available
                            cursor.execute('''
                                UPDATE venues SET name = COALESCE(?, name)
                                WHERE id = ? AND name IS NULL
                            ''', (venue_name, venue_id))
                            if cursor.rowcount > 0:
                                print(f"DEBUG: Updated venue (tips) {venue_id}. Total imported: {total_venues_imported}")
                            else:
                                print(f"DEBUG: No update needed for venue (tips) {venue_id}.")
                    except sqlite3.Error as e:
                        print(f"Error importing venue {venue_id} from tips: {e}")
    except FileNotFoundError:
        print("tips.json not found. Skipping.")
    except Exception as e:
        print(f"Error processing tips.json for venues: {e}")
    
    # From venueRatings
    try:
        with open('venueRatings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"DEBUG: Processing venueRatings.json for venues.")
            for item in data.get('venueLikes', []):
                venue_id = item.get('id')
                venue_name = item.get('name')
                venue_url = item.get('url')

                if venue_id:
                    print(f"DEBUG: Found venue_id (ratings): {venue_id}, name: {venue_name}, url: {venue_url}")
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO venues (id, name, url)
                            VALUES (?, ?, ?)
                        ''', (venue_id, venue_name, venue_url))
                        if cursor.rowcount > 0:
                            total_venues_imported += 1
                            print(f"DEBUG: Inserted venue (ratings) {venue_id}. Total imported: {total_venues_imported}")
                        else: # Update existing entry if new info is available
                            cursor.execute('''
                                UPDATE venues SET name = COALESCE(?, name), url = COALESCE(?, url)
                                WHERE id = ? AND (name IS NULL OR url IS NULL)
                            ''', (venue_name, venue_url, venue_id))
                            if cursor.rowcount > 0:
                                print(f"DEBUG: Updated venue (ratings) {venue_id}. Total imported: {total_venues_imported}")
                            else:
                                print(f"DEBUG: No update needed for venue (ratings) {venue_id}.")
                    except sqlite3.Error as e:
                        print(f"Error importing venue {venue_id} from venueRatings: {e}")
    except FileNotFoundError:
        print("venueRatings.json not found. Skipping.")
    except Exception as e:
        print(f"Error processing venueRatings.json for venues: {e}")

    conn.commit()
    conn.close()
    print(f"Finished importing venues data. Total unique venues imported/updated: {total_venues_imported}")


def import_checkins_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    checkin_files = [f for f in os.listdir('.') if f.startswith('checkins') and f.endswith('.json')]


    


    total_checkins_imported = 0





    for filename in checkin_files:


        print(f"Processing checkins file: {filename}")


        with open(filename, 'r', encoding='utf-8') as f:


            data = json.load(f)


            for item in data.get('items', []):


                checkin_id = item.get('id')


                created_at = item.get('createdAt')


                shout = item.get('shout')


                time_zone = item.get('timeZone')





                venue = item.get('venue', {})


                venue_id = venue.get('id')


                # No longer need venueName, venueAddress, venueLat, venueLng directly in checkins table





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO checkins (id, createdAt, venueId, shout, timeZone)


                        VALUES (?, ?, ?, ?, ?)


                    ''', (checkin_id, created_at, venue_id, shout, time_zone))


                    if cursor.rowcount > 0:


                        total_checkins_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing checkin {checkin_id} from {filename}: {e}")


    


    conn.commit()


    conn.close()


    print(f"Finished importing checkins data. Total checkins imported: {total_checkins_imported}")





def import_photos_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    photo_files = [f for f in os.listdir('.') if f.startswith('photos') and f.endswith('.json')]


    


    total_photos_imported = 0





    for filename in photo_files:


        print(f"Processing photos file: {filename}")


        with open(filename, 'r', encoding='utf-8') as f:


            data = json.load(f)


            for item in data.get('items', []):


                photo_id = item.get('id')


                created_at = item.get('createdAt')


                full_url = item.get('fullUrl')


                width = item.get('width')


                height = item.get('height')


                related_item_url = item.get('relatedItemUrl')





                checkin_id = None


                if related_item_url:


                    match = re.search(r'checkin/([a-f0-9]+)', related_item_url)


                    if match:


                        checkin_id = match.group(1)


                


                local_path = os.path.join(PIX_DIR, f"{photo_id}.jpg") # Assuming all photos are JPG and named by their ID





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO photos (id, checkinId, createdAt, fullUrl, localPath, width, height)


                        VALUES (?, ?, ?, ?, ?, ?, ?)


                    ''', (photo_id, checkin_id, created_at, full_url, local_path, width, height))


                    if cursor.rowcount > 0:


                        total_photos_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing photo {photo_id} from {filename}: {e}")


    


    conn.commit()


    conn.close()


    print(f"Finished importing photos data. Total photos imported: {total_photos_imported}")





def import_users_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()


    


    total_users_imported = 0


    total_friends_imported = 0





    try:


        with open('users.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            


            # Import self user data


            self_user = data.get('self', {})


            if self_user:


                user_id = self_user.get('id')


                firstName = self_user.get('firstName')


                lastName = self_user.get('lastName')


                email = self_user.get('email')


                gender = self_user.get('gender')


                homeCity = self_user.get('homeCity')


                bio = self_user.get('bio')


                


                contact = self_user.get('contact', {})


                phone = contact.get('phone')


                verifiedPhone = contact.get('verifiedPhone') == 'true'


                verifiedEmail = contact.get('verifiedEmail') == 'true'


                facebook = contact.get('facebook')





                photo = self_user.get('photo', {})


                photoPrefix = photo.get('prefix')


                photoSuffix = photo.get('suffix')





                birthday = self_user.get('birthday')


                displayName = self_user.get('displayName')


                tipsCount = self_user.get('tips', {}).get('count')


                listsCount = self_user.get('lists', {}).get('groups', [{}])[0].get('count') # Assuming first group is relevant





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO users (id, firstName, lastName, email, gender, homeCity, bio, phone, verifiedPhone, verifiedEmail, facebook, photoPrefix, photoSuffix, birthday, displayName, tipsCount, listsCount)


                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)


                    ''', (user_id, firstName, lastName, email, gender, homeCity, bio, phone, verifiedPhone, verifiedEmail, facebook, photoPrefix, photoSuffix, birthday, displayName, tipsCount, listsCount))


                    if cursor.rowcount > 0:


                        total_users_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing user {user_id}: {e}")





            # Import friends data


            friends_list = data.get('friends', {}).get('items', [])


            for friend in friends_list:


                friend_id = friend.get('id')


                friend_firstName = friend.get('firstName')


                friend_lastName = friend.get('lastName')


                friend_canonicalUrl = friend.get('canonicalUrl')





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO friends (userId, friendId, friendFirstName, friendLastName, friendCanonicalUrl)


                        VALUES (?, ?, ?, ?, ?)


                    ''', (self_user.get('id'), friend_id, friend_firstName, friend_lastName, friend_canonicalUrl))


                    if cursor.rowcount > 0:


                        total_friends_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing friend {friend_id} for user {self_user.get('id')}: {e}")





    except FileNotFoundError:


        print("users.json not found. Skipping user data import.")


    except Exception as e:


        print(f"Error processing users.json: {e}")





    conn.commit()


    conn.close()


    print(f"Finished importing users data. Total users imported: {total_users_imported}. Total friends imported: {total_friends_imported}")





def import_visits_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('visits.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_visits_imported = 0


            for item in data.get('items', []):


                visit_id = item.get('id')


                userId = item.get('userId')


                timeArrived = item.get('timeArrived')


                timeDeparted = item.get('timeDeparted')


                os = item.get('os')


                osVersion = item.get('osVersion')


                deviceModel = item.get('deviceModel')


                isTraveling = item.get('isTraveling')


                latitude = item.get('latitude')


                longitude = item.get('longitude')


                city = item.get('city')


                state = item.get('state')


                countryCode = item.get('countryCode')


                locationType = item.get('locationType')





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO visits (id, userId, timeArrived, timeDeparted, os, osVersion, deviceModel, isTraveling, latitude, longitude, city, state, countryCode, locationType)


                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)


                    ''', (visit_id, userId, timeArrived, timeDeparted, os, osVersion, deviceModel, isTraveling, latitude, longitude, city, state, countryCode, locationType))


                    if cursor.rowcount > 0:


                        total_visits_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing visit {visit_id}: {e}")


        conn.commit()


        print(f"Finished importing visits data. Total visits imported: {total_visits_imported}")


    except FileNotFoundError:


        print("visits.json not found. Skipping visits data import.")


    except Exception as e:


        print(f"Error processing visits.json: {e}")


    finally:


        conn.close()





def import_unconfirmed_visits_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('unconfirmed_visits.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_unconfirmed_visits_imported = 0


            for item in data.get('items', []):


                visit_id = item.get('id')


                startTime = item.get('startTime')


                endTime = item.get('endTime')


                venueId = item.get('venueId')


                lat = item.get('lat')


                lng = item.get('lng')


                # Removed venueName, venueUrl as they are in the venues table





                try:


                    cursor.execute('''


                                                INSERT OR IGNORE INTO unconfirmed_visits (id, startTime, endTime, venueId, lat, lng)


                                                VALUES (?, ?, ?, ?, ?, ?)


                                            ''', (visit_id, startTime, endTime, venueId, lat, lng))


                    if cursor.rowcount > 0:


                        total_unconfirmed_visits_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing unconfirmed visit {visit_id}: {e}")


        conn.commit()


        print(f"Finished importing unconfirmed visits data. Total unconfirmed visits imported: {total_unconfirmed_visits_imported}")


    except FileNotFoundError:


        print("unconfirmed_visits.json not found. Skipping unconfirmed visits data import.")


    except Exception as e:


        print(f"Error processing unconfirmed_visits.json: {e}")


    finally:


        conn.close()





def import_tips_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('tips.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_tips_imported = 0


            for item in data.get('items', []):


                tip_id = item.get('id')


                createdAt = item.get('createdAt')


                text = item.get('text')


                tip_type = item.get('type')


                canonicalUrl = item.get('canonicalUrl')


                viewCount = item.get('viewCount')


                agreeCount = item.get('agreeCount')


                disagreeCount = item.get('disagreeCount')


                


                user = item.get('user', {})


                userId = user.get('id')





                venue = item.get('venue', {})


                venueId = venue.get('id')


                # Removed venueName as it is in the venues table





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO tips (id, createdAt, text, type, canonicalUrl, viewCount, agreeCount, disagreeCount, userId, venueId)


                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)


                    ''', (tip_id, createdAt, text, tip_type, canonicalUrl, viewCount, agreeCount, disagreeCount, userId, venueId))


                    if cursor.rowcount > 0:


                        total_tips_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing tip {tip_id}: {e}")


        conn.commit()


        print(f"Finished importing tips data. Total tips imported: {total_tips_imported}")


    except FileNotFoundError:


        print("tips.json not found. Skipping tips data import.")


    except Exception as e:


        print(f"Error processing tips.json: {e}")


    finally:


        conn.close()





def import_comments_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('comments.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_comments_imported = 0


            for item in data.get('items', []):


                userId = item.get('userId')


                time = item.get('time')


                comment = item.get('comment')





                try:


                    cursor.execute('''


                        INSERT INTO comments (userId, time, comment)


                        VALUES (?, ?, ?)


                    ''', (userId, time, comment))


                    if cursor.rowcount > 0:


                        total_comments_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing comment from user {userId} at {time}: {e}")


        conn.commit()


        print(f"Finished importing comments data. Total comments imported: {total_comments_imported}")


    except FileNotFoundError:


        print("comments.json not found. Skipping comments data import.")


    except Exception as e:


        print(f"Error processing comments.json: {e}")


    finally:


        conn.close()





def import_venue_ratings_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('venueRatings.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_venue_ratings_imported = 0


            for item in data.get('venueLikes', []): # "venueLikes" is the key here


                venue_id = item.get('id')


                name = item.get('name')


                url = item.get('url')





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO venue_ratings (id, name, url)


                        VALUES (?, ?, ?)


                    ''', (venue_id, name, url))


                    if cursor.rowcount > 0:


                        total_venue_ratings_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing venue rating {venue_id}: {e}")


        conn.commit()


        print(f"Finished importing venue ratings data. Total venue ratings imported: {total_venue_ratings_imported}")


    except FileNotFoundError:


        print("venueRatings.json not found. Skipping venue ratings data import.")


    except Exception as e:


        print(f"Error processing venueRatings.json: {e}")


    finally:


        conn.close()





def import_expertise_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('expertise.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_expertise_imported = 0


            for item in data.get('items', []):


                item_id = item.get('id')


                item_type = item.get('type')


                timestamp = item.get('timestamp')


                lastModified = item.get('lastModified')





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO expertise (id, type, timestamp, lastModified)


                        VALUES (?, ?, ?, ?)


                    ''', (item_id, item_type, timestamp, lastModified))


                    if cursor.rowcount > 0:


                        total_expertise_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing expertise {item_id}: {e}")


        conn.commit()


        print(f"Finished importing expertise data. Total expertise imported: {total_expertise_imported}")


    except FileNotFoundError:


        print("expertise.json not found. Skipping expertise data import.")


    except Exception as e:


        print(f"Error processing expertise.json: {e}")


    finally:


        conn.close()





def import_plans_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('plans.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_plans_imported = 0


            for item in data.get('items', []):


                plan_id = item.get('id')


                userId = item.get('userId')


                createdAt = item.get('createdAt')


                modifiedTime = item.get('modifiedTime')


                isBroadcast = item.get('isBroadcast')


                plan_type = item.get('type')





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO plans (id, userId, createdAt, modifiedTime, isBroadcast, type)


                        VALUES (?, ?, ?, ?, ?, ?)


                    ''', (plan_id, userId, createdAt, modifiedTime, isBroadcast, plan_type))


                    if cursor.rowcount > 0:


                        total_plans_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing plan {plan_id}: {e}")


        conn.commit()


        print(f"Finished importing plans data. Total plans imported: {total_plans_imported}")


    except FileNotFoundError:


        print("plans.json not found. Skipping plans data import.")


    except Exception as e:


        print(f"Error processing plans.json: {e}")


    finally:


        conn.close()





def import_shares_data():


    conn = sqlite3.connect(DATABASE_NAME)


    cursor = conn.cursor()





    try:


        with open('shares.json', 'r', encoding='utf-8') as f:


            data = json.load(f)


            total_shares_imported = 0


            for item in data.get('items', []):


                share_id = item.get('id')


                sharedAt = item.get('sharedAt')


                state = item.get('state')


                share_type = item.get('type')





                try:


                    cursor.execute('''


                        INSERT OR IGNORE INTO shares (id, sharedAt, state, type)


                        VALUES (?, ?, ?, ?)


                    ''', (share_id, sharedAt, state, share_type))


                    if cursor.rowcount > 0:


                        total_shares_imported += 1


                except sqlite3.Error as e:


                    print(f"Error importing share {share_id}: {e}")


        conn.commit()


        print(f"Finished importing shares data. Total shares imported: {total_shares_imported}")


    except FileNotFoundError:


        print("shares.json not found. Skipping shares data import.")


    except Exception as e:


        print(f"Error processing shares.json: {e}")


    finally:


        conn.close()








def main():








    setup_database()








    import_venues_data() # Ensure venues are imported first








    import_checkins_data()








    import_photos_data()








    import_users_data()








    import_visits_data()








    import_unconfirmed_visits_data()








    import_tips_data()








    import_comments_data()








    import_venue_ratings_data()








    import_expertise_data()








    import_plans_data()








    import_shares_data()








    print("Data import process completed.")





if __name__ == '__main__':


    main()
