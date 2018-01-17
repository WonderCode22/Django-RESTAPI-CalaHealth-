# Goal of Project
Develop RESTful API to send database data to FE which is built in React

# Login
Used PyJWT for authentication

#Environment Setup
1. Install pip and virtualenv
2. Create your env and activate it
3. Install PostgreSQL and create cala_health database.
4. Modify the SQLALCHEMY_DATABASE_URI variable of DevelopmentConfig Class in Configurations.py like below
    
        SQLALCHEMY_DATABASE_URI = 'postgresql://[username]:[password]@localhost/cala_health'
       
5. Install required packages
        
         python install setup.py

6. Run Project
        
         python run.py runserver
      
