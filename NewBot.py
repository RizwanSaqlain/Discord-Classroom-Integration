from __future__ import print_function

import os
import os.path
import discord
import json
import googleapiclient.discovery
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icecream import ic
from functools import lru_cache
import mysql.connector

from configuration import *

#conn imported from configuration
cursor = conn.cursor()

#os.remove('token.json')     #ONLY TO BE USED WHEN CHANGING SCOPES OR JUST DELETE token.json AFTER CHANGING

SCOPES = [
    'https://www.googleapis.com/auth/classroom.announcements',
    'https://www.googleapis.com/auth/classroom.courses',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials',
]
################################################    VARIABLES      ########################################################


# Discord bot token
discordBotToken = os.getenv('DISCORD_BOT_TOKEN')

#Rest Added to configuration.py

########################################   LOADING UP CREDENTIALS   ####################################################
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.

# If there are no (valid) credentials available, let the user log in.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except:
            flow = InstalledAppFlow.from_client_secrets_file(
            'D:\\Programming\\Python File\\workspace\\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'D:\\Programming\\Python File\\workspace\\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


#########################################################    APIS     #######################################################################


# Discord client API
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)


# Set up the Google Classroom API client
service = build("classroom", "v1", credentials=creds)

#########################################################  FUNCTIONS   ####################################################################

@lru_cache(maxsize=20)
def getTeachers(courseId):
    teachers_response = service.courses().teachers().list(courseId=courseId).execute()
    teachers = teachers_response.get('teachers', [])
    return teachers

@lru_cache(maxsize=20)
def getStudents(courseId):
    students_response = service.courses().students().list(courseId=courseId).execute()
    students = students_response.get('students', [])
    return students


def getAnnouncements(courseId):
    announcements_response = service.courses().announcements().list(courseId=courseId).execute()  
    announcements = announcements_response.get("announcements", [])
    return announcements


def getCourseWork(courseId):
    courseWorks_response = service.courses().courseWork().list(courseId=courseId).execute()
    courseWorks = courseWorks_response.get('courseWork', [])
    return courseWorks


def getCourseWorkMaterials(courseId):
    courseWorksMaterials_response = service.courses().courseWorkMaterials().list(courseId=courseId).execute()
    courseWorkMaterials = courseWorksMaterials_response.get('courseWorkMaterial', [])
    return courseWorkMaterials

def format_datetime(datetime_str):
    datetimeObject = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_datetime_str = datetimeObject.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_datetime_str

def insertDataAnnouncement(announcement):
    courseId = announcement['courseId']
    announcementId = announcement['id']
    text = announcement['text']
    state = announcement['state']
    alternateLink = announcement['alternateLink']
    creationTime = format_datetime(announcement['creationTime'])
    updateTime = format_datetime(announcement['updateTime'])
    creatorUserId = announcement['creatorUserId']
    materials = None
    try:
        if 'materials' in announcement:
            for material in announcement['materials']:
                material = material['driveFile']
                materials = json.dumps(material)
    except KeyError:
        pass

    query = "INSERT INTO announcements (CourseID, AnnouncementID, Text, Materials, State, alternateLink, creationTime, updateTime, creatorUserId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query,(courseId, announcementId, text, materials, state, alternateLink, creationTime, updateTime, creatorUserId))
    conn.commit()

def insertDataCourseWork(courseWork):
    courseId = courseWork['courseId']
    courseWorkId = courseWork['id']
    title = courseWork['title']
    state = courseWork['state']
    alternateLink = courseWork['alternateLink']
    creationTime = format_datetime(courseWork['creationTime'])
    updateTime = format_datetime(courseWork['updateTime'])
    maxPoints = courseWork['maxPoints']
    workType = courseWork["workType"]
    submissionModificationMode = courseWork['submissionModificationMode']
    creatorUserId = courseWork['creatorUserId']

    query = "INSERT INTO courseWorks (courseId, courseWorkId, title, state, alternateLink, creationTime, updateTime, maxPoints, workType, submissionModificationMode, creatorUserId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query,(courseId, courseWorkId, title, state, alternateLink, creationTime, updateTime, maxPoints, workType, submissionModificationMode, creatorUserId))
    conn.commit()

def insertDatacourseWorkMaterial(courseWorkMaterial):
    courseId = courseWorkMaterial['courseId']
    courseWorkMaterialId = courseWorkMaterial['id']
    title = courseWorkMaterial['title']
    state = courseWorkMaterial['state']
    alternateLink = courseWorkMaterial['alternateLink']
    creationTime = format_datetime(courseWorkMaterial['creationTime'])
    updateTime = format_datetime(courseWorkMaterial['updateTime'])
    creatorUserId = courseWorkMaterial['creatorUserId']
    materials = None
    description = None
    try:
        if 'materials' in courseWorkMaterial:
            for material in courseWorkMaterial['materials']:
                material = material['driveFile']
                materials = json.dumps(material)
        if 'description' in courseWorkMaterial:
            description = courseWorkMaterial['description']

    except KeyError:
        pass

    query = "INSERT INTO courseWorkMaterials (courseId, courseWorkMaterialId, title, description ,materials, state, alternateLink, creationTime, updateTime, creatorUserId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query,(courseId, courseWorkMaterialId, title, description, materials, state, alternateLink, creationTime, updateTime, creatorUserId))
    conn.commit()

def searchInTable(searchTerm, tableName,column):
    query = f"SELECT * FROM {tableName} WHERE LOWER({column}) LIKE LOWER(%s)"
    cursor.execute(query,(f"%{searchTerm}%",))
    results = cursor.fetchall()
    return results


async def sendAnnouncements(courseId, channelIdAnnouncement, channelId, ClassName):
    announcements = getAnnouncements(courseId)
    if not announcements:
        print("No announcements for {}".format(ClassName))
        return
        
    teachers = getTeachers(courseId)
    students = getStudents(courseId)
        
    query = f"SELECT announcementId FROM announcements WHERE courseId={courseId};"
    cursor.execute(query)
    results = cursor.fetchall()
    result_list = [item[0] for item in results]
    for announcement in announcements:
        if announcement['id'] in result_list:
            continue
        
        ic(announcement)
        insertDataAnnouncement(announcement)
        
        user_id = announcement["creatorUserId"]
        title=announcement['text']
        desc= 'Automated message sent through Google Classroom API. This message is from {} Classroom. Head to <#{}> for more info'.format(ClassName, channelId)

        if len(title) >= 255:
            desc, title = title , desc
            
        embed = discord.Embed(title=title, description=desc)
        embed.set_author(name="Unknown Author")
        for teacher in teachers:
            if user_id == teacher['userId']:
                # icon_url=teacher['profile']['photoUrl'] not functional until non-http urls are accepted as icon_url
                embed.set_author(name=teacher['profile']['name']['fullName'])
                break

        for student in students:
            if user_id == student['userId']:
                # icon_url=student['profile']['photoUrl'] not functional until non-http urls are accepted as icon_url
                embed.set_author(name=student['profile']['name']['fullName'])
                break

        embed.color = discord.Color.dark_blue()
        await client.get_channel(channelIdAnnouncement).send(embed=embed)
        print("Announcement for {} sent.".format(ClassName))

        if 'materials' not in announcement:
            title=announcement['text']
            desc= 'This message had no attachments'

            if len(title) >= 255:
                desc, title = title , desc

            embed = discord.Embed(title=title, description=desc)
            user_id = announcement["creatorUserId"]
            embed.set_author(name="Unknown Author")
            for teacher in teachers:
                if user_id == teacher['userId']:
                    embed.set_author(name=teacher['profile']['name']['fullName'])
                    break

            for student in students:
                if user_id == student['userId']:
                    embed.set_author(name=student['profile']['name']['fullName'])
                    break
        
            embed.color = discord.Color.dark_blue()
            await client.get_channel(channelId).send(embed=embed)
            print("Announcements Send but no attachments")
            continue

        for material in announcement["materials"]:
            try:
                file_name = material["driveFile"]["driveFile"]["title"]
            except KeyError as error:
                file_name = 'Undefined'
                print(error)
            file_id = material["driveFile"]["driveFile"]["id"]
            file_url = material["driveFile"]["driveFile"]['alternateLink']
            title=announcement['text']
            desc= f"File Link:{file_url} \nFile Name: {file_name}"

            if len(title) >= 255:
                desc, title = title , desc

            embed = discord.Embed(title=title, description=desc)
            try:
                file_name = material["driveFile"]["driveFile"]["title"]
            except KeyError as error:
                file_name = 'Undefined'
                print(error)
            
            try:
                thumbnail_url = material["driveFile"]["driveFile"]["thumbnailUrl"]
                embed.set_image(url=thumbnail_url)
            except KeyError as error:
                print(error)
                pass
                
            channel = client.get_channel(channelId)
            user_id = announcement["creatorUserId"]
            embed.set_author(name="Unknown Author")
            for teacher in teachers:
                if user_id == teacher['userId']:
                    embed.set_author(name=teacher['profile']['name']['fullName'])
                    break

            for student in students:
                if user_id == student['userId']:
                    embed.set_author(name=student['profile']['name']['fullName'])
                    break

            embed.color = discord.Color.dark_magenta()
            
            await channel.send(embed=embed)
            print("File successfully sent : "+file_name)



async def sendCourseWork(courseId, channelIdAnnouncement, channelId, ClassName):
    courseWorks = getCourseWork(courseId)
    if not courseWorks:
        print("No Courseworks for {}".format(ClassName))
        return
    
    teachers = getTeachers(courseId)
    students = getStudents(courseId)
    
    query = f"SELECT courseWorkId FROM courseWorks WHERE courseId={courseId};"
    cursor.execute(query)
    results = cursor.fetchall()
    result_list = [item[0] for item in results]

    for courseWork in courseWorks:
        if courseWork['id'] in result_list:
            continue
        
        ic(courseWork)
        insertDataCourseWork(courseWork)

        user_id = courseWork["creatorUserId"]
        title=courseWork['title']
        desc= 'Automated message sent through Google Classroom API. This message is from {} Classroom. Head to <#{}> for more info'.format(ClassName, channelId)
        embed = discord.Embed(title=title, description=desc)
        embed.set_author(name="Unknown Author")
        for teacher in teachers:
            if user_id == teacher['userId']:
                # icon_url=teacher['profile']['photoUrl'] not functional until non-http urls are accepted as icon_url
                embed.set_author(name=teacher['profile']['name']['fullName'])
                break

        for student in students:
            if user_id == student['userId']:
                # icon_url=student['profile']['photoUrl'] not functional until non-http urls are accepted as icon_url
                embed.set_author(name=student['profile']['name']['fullName'])
                break

        embed.color = discord.Color.dark_blue()
        await client.get_channel(channelIdAnnouncement).send(embed=embed)
        print("Coursework for {} sent.".format(ClassName))

        if 'materials' not in courseWork:
            workType = courseWork["workType"]
            maxpoints = courseWork['maxPoints']
            alternateLink = courseWork['alternateLink']
            embed = discord.Embed(title=title, description=f"WorkType: {workType} \nMax Points: {maxpoints} \nClassroom Link: {alternateLink}")
            user_id = courseWork["creatorUserId"]
            embed.set_author(name="Unknown Author")
            for teacher in teachers:
                if user_id == teacher['userId']:
                    embed.set_author(name=teacher['profile']['name']['fullName'])
                    break

            for student in students:
                if user_id == student['userId']:
                    embed.set_author(name=student['profile']['name']['fullName'])
                    break

            embed.color = discord.Color.dark_blue()
            await client.get_channel(channelId).send(embed=embed)
            print("CourseWorks Send but no attachments")
            continue

        for material in courseWork["materials"]:
            file_id = material["driveFile"]["driveFile"]["id"]
            file_url = material["driveFile"]["driveFile"]['alternateLink']
            file_name = material["driveFile"]["driveFile"]["title"]
            user_id = courseWork["creatorUserId"]

            channel = client.get_channel(channelId)
            embed = discord.Embed(title=title, description=file_url)
            embed.set_author(name="Unknown Author")
            for teacher in teachers:
                if user_id == teacher['userId']:
                    embed.set_author(name=teacher['profile']['name']['fullName'])
                    break

            for student in students:
                if user_id == student['userId']:
                    embed.set_author(name=student['profile']['name']['fullName'])
                    break

            embed.color = discord.Color.dark_magenta()
            await channel.send(embed=embed)
            print("File successfully sent : "+file_name)

async def sendCourseWorkMaterials(courseId, channelIdAnnouncement, channelId, ClassName):
    courseWorkMaterials = getCourseWorkMaterials(courseId)
    if not courseWorkMaterials:
        print("No CourseworkMaterials for {}".format(ClassName))
        return
    
    teachers = getTeachers(courseId)
    students = getStudents(courseId)


    query = f"SELECT courseWorkMaterialId FROM courseWorkMaterials WHERE courseId={courseId};"
    cursor.execute(query)
    results = cursor.fetchall()
    result_list = [item[0] for item in results]

    for courseWorkMaterial in courseWorkMaterials:
        if courseWorkMaterial['id'] in result_list:
            continue
        
        ic(courseWorkMaterial)
        insertDatacourseWorkMaterial(courseWorkMaterial)

        user_id = courseWorkMaterial["creatorUserId"]
        embed = discord.Embed(
            title=courseWorkMaterial['title'], description='Automated message sent through Google Classroom API. This message is from {} Classroom. Head to <#{}> for more info'.format(ClassName, channelId))
        embed.set_author(name="Unknown Author")
        for teacher in teachers:
            if user_id == teacher['userId']:
                # icon_url=teacher['profile']['photoUrl'] not functional until non-http urls are accepted as icon_url
                embed.set_author(name=teacher['profile']['name']['fullName'])
                break

        for student in students:
            if user_id == student['userId']:
                # icon_url=student['profile']['photoUrl'] not functional until non-http urls are accepted as icon_url
                embed.set_author(name=student['profile']['name']['fullName'])
                break

        embed.color = discord.Color.dark_blue()
        await client.get_channel(channelIdAnnouncement).send(embed=embed)
        print("CourseworkMaterials for {} sent.".format(ClassName))

        if 'description' not in courseWorkMaterial:
                courseWorkMaterial['description'] = None

        if 'materials' not in courseWorkMaterial:
            embed = discord.Embed(
                title=courseWorkMaterial['title'], description=f'{courseWorkMaterial['description']}\nThis message had no attachments')
            user_id = courseWorkMaterial["creatorUserId"]
            embed.set_author(name="Unknown Author")
            for teacher in teachers:
                if user_id == teacher['userId']:
                    embed.set_author(
                        name=teacher['profile']['name']['fullName'])
                    break

            for student in students:
                if user_id == student['userId']:
                    embed.set_author(
                        name=student['profile']['name']['fullName'])
                    break

            embed.color = discord.Color.dark_blue()
            await client.get_channel(channelId).send(embed=embed)
            print("CourseWorkMaterials Send but no attachments")
            continue

        for material in courseWorkMaterial["materials"]:

            file_id = material["driveFile"]["driveFile"]["id"]
            file_url = material["driveFile"]["driveFile"]['alternateLink']
            file_name = courseWorkMaterial['title']
            user_id = courseWorkMaterial["creatorUserId"]

            # Send the file to the Discord channel
            channel = client.get_channel(channelId)
            embed = discord.Embed(
                title=courseWorkMaterial['title'], description=f'Description: {courseWorkMaterial['description']}\nFile Link: {file_url}')
            embed.set_author(name="Unknown Author")
            for teacher in teachers:
                if user_id == teacher['userId']:
                    embed.set_author(
                        name=teacher['profile']['name']['fullName'])
                    break

            for student in students:
                if user_id == student['userId']:
                    embed.set_author(
                        name=student['profile']['name']['fullName'])
                    break

            embed.color = discord.Color.dark_magenta()

            await channel.send(embed=embed)
            print("File successfully sent : "+file_name)


async def sendResponse(courseId, channelIdAnnouncement, channelId, ClassName):
    await sendAnnouncements(courseId, channelIdAnnouncement, channelId, ClassName)
    await sendCourseWork(courseId, channelIdAnnouncement, channelId, ClassName)
    await sendCourseWorkMaterials(courseId, channelIdAnnouncement, channelId, ClassName)

async def sendSearchEmbed_Announcement(result,channel,searchTerm):
    for row in result:
        courseId = row[0]
        text = row[2]
        title = text
        json_data = json.loads(row[3])
        materialLink = json_data['driveFile']['alternateLink']
        materialTitle = None
        try:
            materialTitle = json_data['driveFile']['title']
        except KeyError:
            pass
        classroomLink = row[5]
        user_id = row[8]
        desc = f"Title:{materialTitle} \nMaterial Link: {materialLink} \nGoogle ClassRoom Link: {classroomLink}"
        if len(title) >= 255:
            desc, title = title , desc
        embed = discord.Embed(
            title=title, description=desc
        )
        embed.set_author
        embed.set_author(name="Unknown Author")
        teachers = getTeachers(courseId)
        students = getStudents(courseId)
        for teacher in teachers:
            if user_id == teacher['userId']:
                embed.set_author(
                    name=teacher['profile']['name']['fullName'])
                break

        for student in students:
            if user_id == student['userId']:
                embed.set_author(
                    name=student['profile']['name']['fullName'])
                break

        embed.color = discord.Color.dark_magenta()
        await channel.send(embed=embed)
    print(f"A total of {len(result)} search results were sent for search term: '{searchTerm}' in Announcements")
    await channel.send(f"A total of {len(result)} search results were sent for search term '{searchTerm}' in Announcements")

async def sendSearchEmbed_CourseWorkMaterial(result,channel,searchTerm):
    for row in result:
        courseId = row[0]
        title = row[2]
        description = row[3]
        if row[4] is None:
            print("No material for search term")
            await channel.send(f"No material for search term: {searchTerm}")
            return
        json_data = json.loads(row[4])
        materialLink = json_data['driveFile']['alternateLink']
        classroomLink = row[6]
        user_id = row[9]
        embed = discord.Embed(
            title=title, description=f"Description: {description} \nMaterial Link: {materialLink} \nGoogle ClassRoom Link: {classroomLink}"
        )
        embed.set_author
        embed.set_author(name="Unknown Author")
        teachers = getTeachers(courseId)
        students = getStudents(courseId)
        for teacher in teachers:
            if user_id == teacher['userId']:
                embed.set_author(
                    name=teacher['profile']['name']['fullName'])
                break

        for student in students:
            if user_id == student['userId']:
                embed.set_author(
                    name=student['profile']['name']['fullName'])
                break

        embed.color = discord.Color.dark_magenta()
        await channel.send(embed=embed)
    print(f"A total of {len(result)} search results were sent for search term: '{searchTerm}' in CourseWork Materials")
    await channel.send(f"A total of {len(result)} search results were sent for search term '{searchTerm}' in CourseWork Materials")

# Set up the Discord client
@client.event
async def on_ready():
    print(f"{client.user.name} is connected to Discord!")


@client.event
async def on_message(message):
    channel = message.channel
    if message.author == client.user:
        return
    
    if message.author.id != myauthid and (message.content == '!shutdown' or message.content == '!run'):
        print("Unauthorised access tried by user:{} ".format(message.author.name))
        await channel.send("You do not have access to run this command...")

    if message.content.startswith('!hello'):
        await channel.send(f'Hello {message.author.mention}')
    
    if message.author.id == myauthid:
        if message.content == '!run':
            await sendResponse(courseIdFC, channelIdTesting, channelIdTesting, "Fundamentals of Computing")
            await sendResponse(courseIdSessional, channelIdTesting, channelIdTesting, "Sessional Papers")
            await sendResponse(courseIdComputerOrganization, channelIdAnnouncement, channelIdComputerOrganization, "Computer Organization")
            await channel.send("All commands ran successfully")
        if message.content == '!shutdown':
            await channel.send("Shutting down")
            cursor.close()
            conn.close()
            time.sleep()
            print("shutdown")
            await client.close()
        if message.content.startswith("!search"):
            searchTerm = message.content.removeprefix("!search ")
            result = searchInTable(searchTerm, "courseWorkMaterials", "title")
            await sendSearchEmbed_CourseWorkMaterial(result,channel, searchTerm)
        if message.content.startswith("!find"):
            searchTerm = message.content.removeprefix("!find ")
            result = searchInTable(searchTerm, "announcements", "materials")
            await sendSearchEmbed_Announcement(result,channel, searchTerm)
        

client.run(discordBotToken)


