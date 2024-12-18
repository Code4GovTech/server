from utils.db import PostgresORM, SupabaseInterface
from datetime import datetime

class MigrateContributors:
    def __init__(self):
        self.postgres_client = PostgresORM.get_instance()
        self.supabase_client = SupabaseInterface.get_instance()
        return
    
    async def migration(self):
        try:
            #migrate contributors discord
            await self.migrate_contributors_discord()
            
            #migrate contributors registraiton
            await self.migrate_contributors_registration()
            
            return 'success'
        
        except Exception as e:
            print('Exception occured while migrating users ', e)
            return 'failed'
        
    def convert_to_datetime(self, date_str):
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        return dt.replace(tzinfo=None)

    async def migrate_contributors_discord(self):
        try:
            supabase_contributors_discord = self.supabase_client.readAll("contributors_discord")
            postgres_contributors_discord = await self.postgres_client.readAll("contributors_discord")
            print('length of supabase_contributors_discord ', len(supabase_contributors_discord))
            print('length of postgres_contributors_discord ', len(postgres_contributors_discord))
            
            for contributor in supabase_contributors_discord:
                # Ensure the correct key is used to compare 'discord_id' values.
                discord_id = contributor['discord_id']
                present = next((pcd for pcd in postgres_contributors_discord if pcd['discord_id'] == discord_id), None)

                if present:
                    continue
                else:
                    #insert the record in postgres
                    # format = ''
                    print('inserting contributors discord for ', contributor['discord_id'])

                    contributors_data = {
                        'github_url': contributor['github_url'],
                        'discord_id': contributor['discord_id'],
                        'discord_username': contributor['discord_username'],
                        'joined_at': self.convert_to_datetime(contributor['joined_at']),
                        'email': contributor['email'],
                        'chapter': contributor['chapter'],
                        'gender': contributor['gender'],
                        'is_active': contributor['is_active'],
                        'country': contributor['country'],
                        'city': contributor['city'],
                        'experience': contributor['experience'],
                        'field_name': contributor['name']
                    }
                    await self.postgres_client.add_data(contributors_data, "contributors_discord")
                        
            return 'success'
                    
        except Exception as e:
            print('Exception occured while migrate contributors discord ', e)
            return 'failed'
        
    

    async def migrate_contributors_registration(self):
        try:
            supabase_contributors_registration = self.supabase_client.readAll("contributors_registration")
            postgres_contributors_registration = await self.postgres_client.readAll("contributors_registration")

            print('length of supabase_contributors_registration ', len(supabase_contributors_registration))
            print('length of postgres_contributors_registration ', len(postgres_contributors_registration))
            
            for contributor in supabase_contributors_registration:
                # Ensure the correct key is used to compare 'discord_id' values.
                discord_id = contributor['discord_id']
                present = next((pcd for pcd in postgres_contributors_registration if pcd['discord_id'] == discord_id), None)

                if present:
                    continue
                else:
                    #insert the record in postgres
                    print('inserting contributors discord for ', contributor['discord_id'])
                    contributors_data = {
                        'discord_id': contributor['discord_id'],
                        'github_id': contributor['github_id'],
                        'github_url': contributor['github_url'],
                        'discord_username': contributor['discord_username'],
                        'joined_at': self.convert_to_datetime(contributor['joined_at']),
                        'email': contributor['email'],
                        'name': contributor['name']
                    }
                    await self.postgres_client.add_data(contributors_data, "contributors_registration")
                        
            return 'success'
                    
        except Exception as e:
            print('Exception occured while migrate contributors discord ', e)
            return 'failed'