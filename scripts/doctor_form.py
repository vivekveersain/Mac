import time
import random
import requests

name_options = [
    "Aarav", "Aditya", "Aryan", "Arjun", "Bhavesh", "Chirag", "Darshan", 
    "Dev", "Gaurav", "Harsh", "Ishan", "Jay", "Karan", "Krish", "Manish", 
    "Nikhil", "Om", "Pranav", "Rahul", "Rohan", "Sameer", "Sanjay", 
    "Siddharth", "Tanmay", "Uday", "Varun", "Vikram", "Yash", "Aman", 
    "Deepak", "Ganesh", "Hemant", "Jatin", "Kunal", "Lokesh", "Mohit", 
    "Parth", "Raj", "Ravi", "Shubham", "Tushar", "Vinay", "Akshay", 
    "Bhanu", "Chaitanya", "Dinesh", "Eshan", "Gopal", "Harshit", 
    "Ishaan", "Jayesh", "Kishore", "Lalit", "Manoj", "Nilesh", 
    "Ojas", "Pratik", "Rajesh", "Sandeep", "Tanish", "Vikas", 
    "Yogesh", "Ayaan", "Balaji", "Chaitanya", "Devansh", "Eklavya", 
    "Firoz", "Ganesh", "Harish", "Iqbal", "Jagdish", "Kaushik", 
    "Laxman", "Mohan", "Nitin", "Omkar", "Pradeep", "Qadir", 
    "Raghav", "Sahil", "Tejas", "Umesh", "Vinod", "Akash", 
    "Bhargav", "Chandresh", "Deepesh", "Ekansh", "Ganpat", 
    "Harivansh", "Ishar", "Jai", "Keshav", "Lakshay", "Madan", 
    "Nagesh", "Pankaj", "Qasim", "Ravi", "Sandeep", "Taran", 
    "Vinay", "Aashish", "Bhuvan", "Chiranjeevi", "Dhruv", "Eshwar", 
    "Farhan", "Govind", "Hitesh", "Jeet", "Keshav", "Lakshay", 
    "Madan", "Nagesh", "Pankaj", "Qasim", "Raghav", "Sandeep", 
    "Taran", "Vinod", "Alisha", "Bhavika", "Chahna", "Damini", 
    "Eesha", "Farah", "Gayatri", "Himani", "Jyoti", "Karuna", 
    "Laxmi", "Meenal", "Neelima", "Ojasvi", "Padmini", 
    "Quadirah", "Rupal", "Shalini", "Tejal", "Urmila", 
    "Vishwa", "Wilma", "Yamini", "Aakanksha", "Charvi", 
    "Diya", "Ekisha", "Fatema", "Geeta", "Hiral", "Ishta", 
    "Jaya", "Kanika", "Lavika", "Madhavi", "Namita", 
    "Oorja", "Pallavi", "Ranjana", "Shreya", "Tania", 
    "Varsha", "Wafa", "Yashika", "Zainab", "Aditi", 
    "Ananya", "Anjali", "Avantika", "Bhavna", "Charulata", 
    "Deepa", "Ekta", "Gauri", "Hemlata", "Ishita", "Kavita", 
    "Kirti", "Lavanya", "Meera", "Neha", "Nidhi", "Pooja", 
    "Priya", "Riya", "Sanya", "Sneha", "Tanvi", "Urvashi", 
    "Vani", "Vidya", "Aishwarya", "Chitra", "Dhara", 
    "Elina", "Fatima", "Garima", "Indira", "Kamini", 
    "Lata", "Mansi", "Nandini", "Pallavi", "Radhika", 
    "Sakshi", "Tamanna", "Vaishali", "Yashika", "Zoya", 
    "Aakriti", "Bela", "Chandni", "Devika", "Eshita", 
    "Gitali", "Hirva", "Isha", "Jashvi", "Kaira", 
    "Lina", "Mira", "Navya", "Oviya", "Prisha", 
    "Rhea", "Saanvi", "Tanisha", "Urja", "Vanshika", 
    "Wisha", "Yashvi", "Zaina", "Anushka", "Sita", 
    "Taruna", "Naina", "Neelam", "Komal", "Nisha", 
    "Ritika", "Shobha", "Vijaya", "Amaya", "Bhavini", 
    "Chandrika", "Diksha", "Esha", "Falguni", "Gulshan", 
    "Harini", "Ida", "Juhi", "Kavya", "Lakshmi", 
    "Malati", "Nirmala", "Padma", "Rakhi", "Suman", 
    "Vimla", "Yogita", "Akshara", "Chaitali", "Dhruti", 
    "Geetanjali", "Harmoni", "Kanak", "Lavina", "Meghana", 
    "Nalini", "Padmavati", "Rupali", "Shalini", "Tanushree", 
    "Usha", "Vaijanti", "Yashoda", "Zara", "Aarohi", 
    "Aditi", "Ankita", "Bhakti", "Chandini", "Devyani", 
    "Esha", "Garima", "Hema", "Irani", "Jasleen", 
    "Kajal", "Lavina", "Mahira", "Neha", "Ojasvi", 
    "Purnima", "Quinty", "Ritika", "Sakshi", "Tanisha", 
    "Urmila", "Varsha", "Vishwa", "Wamika", "Yasmin", 
    "Zoya", "Adhira", "Bhavana", "Chhavi", "Disha", 
    "Eshita", "Gauri", "Hemangi", "Indu", "Janvi", 
    "Kanika", "Laksha", "Madhura", "Nandita", "Palak", 
    "Riddhi", "Shriya", "Tanya", "Ujjwala", "Vasudha", 
    "Yamini", "Zeenat", "Aaravi", "Bhavya", "Charita", 
    "Dharini", "Eshwari", "Gunjan", "Indira", "Kiran", 
    "Laxmi", "Meher", "Naina", "Pallavi", "Richa", 
    "Shweta", "Tanvi", "Vaishali", "Yashoda", "Zahra", 
    "Abha", "Bansari", "Chanda", "Deepali", "Eesha", 
    "Falguni", "Gopika", "Hiral", "Ishita", "Jyoti", 
    "Kiran", "Lavanya", "Minal", "Nikita", "Opal", 
    "Poonam", "Rashmi", "Sakhi", "Tanvi", "Usha", 
    "Vaishnavi", "Yasmin", "Ziya", "Aditi", "Anika", 
    "Bhagya", "Chhaya", "Dharini", "Ekta", "Gunjan", 
    "Himalaya", "Ikra", "Jaya", "Kavya", "Lalita", 
    "Manjari", "Naina", "Oorja", "Padma", "Ritika", 
    "Sejal", "Tanya", "Urmila", "Vasudha", "Wafaa", 
    "Yamuna", "Zoya", "Aadya", "Bhavna", "Chaitali", 
    "Deepika", "Elina", "Fathima", "Gowri", "Hiral", 
    "Ikshita", "Janaki", "Kashvi", "Lavina", "Madhuri", 
    "Niharika", "Oviya", "Prisha", "Riya", "Sanjana", 
    "Tanisha", "Vanya", "Wanda", "Yashvi", "Zahra", 
    "Aaravi", "Bhavika", "Charul", "Divya", "Eshana", 
    "Falguni", "Gitali", "Harini", "Isha", "Juhi", 
    "Kajal", "Lata", "Meghana", "Naina", "Ojaswi", 
    "Padmini", "Rupal", "Sreeja", "Tanvi", "Uma", 
    "Vaijanti", "Yamini", "Zohra", "Anvita", "Bhanvi", 
    "Chhavi", "Diya", "Eshita", "Gaurika", "Hema", 
    "Irsha", "Kashish", "Lavanya", "Mamata", "Nishtha", 
    "Pallavi", "Ruchi", "Suman", "Tina", "Urmila", 
    "Vijaya", "Yashvi", "Zeenat", "Adrika", "Bhakti", 
    "Chhaya", "Divya", "Eesha", "Falguni", "Gulshan", 
    "Harini", "Indira", "Jasmin", "Kamala", "Laxmi", 
    "Manya", "Neeti", "Oviya", "Palak", "Radhika", 
    "Sana", "Tara", "Udita", "Vinita", "Yamini", 
    "Zara", "Aaravi", "Bhavya", "Chitra", "Deepali", 
    "Ekisha", "Fatima", "Geeta", "Hiral", "Ishta", 
    "Jaya", "Kanika", "Lavanya", "Meenal", "Nikita", 
    "Oorja", "Poonam", "Radhika", "Shreya", "Tanya", 
    "Urja", "Vaishali", "Yashasvi", "Zara", "Aditi", 
    "Ananya", "Anika", "Avantika", "Bhavna", "Chhavi", 
    "Deepa", "Eesha", "Gauri", "Hemlata", "Ishita", 
    "Kavita", "Kirti", "Lavanya", "Meera", "Neha", 
    "Nidhi", "Pooja", "Priya", "Riya", "Sanya", 
    "Sneha", "Tanvi", "Urvashi", "Vani", "Vidya", 
    "Aishwarya", "Chitra", "Dhara", "Elina", "Fatima", 
    "Garima", "Indira", "Kamini", "Lata", "Mansi", 
    "Nandini", "Pallavi", "Radhika", "Sakshi", "Tamanna", 
    "Vaishali", "Yashika", "Zoya", "Aarav", "Aditya", 
    "Aryan", "Arjun", "Bhavesh", "Chirag", "Darshan", 
    "Dev", "Gaurav", "Harsh", "Ishan", "Jay", 
    "Karan", "Krish", "Manish", "Nikhil", "Om", 
    "Pranav", "Rahul", "Rohan", "Sameer", "Sanjay", 
    "Siddharth", "Tanmay", "Uday", "Varun", "Vikram", 
    "Yash", "Aman", "Deepak", "Ganesh", "Hemant", 
    "Jatin", "Kunal", "Lokesh", "Mohit", "Parth", 
    "Raj", "Ravi", "Shubham", "Tushar", "Vinay", 
    "Akshay", "Bhanu", "Chaitanya", "Dinesh", "Eshan", 
    "Gopal", "Harshit", "Ishaan", "Jayesh", "Kishore", 
    "Lalit", "Manoj", "Nilesh", "Ojas", "Pratik", 
    "Rajesh", "Sandeep", "Taran", "Vinod", "Akash", 
    "Bhargav", "Chandresh", "Deepesh", "Ekansh", "Ganpat", 
    "Harivansh", "Ishar", "Jai", "Keshav", "Lakshay", 
    "Madan", "Nagesh", "Pankaj", "Qasim", "Ravi", 
    "Sandeep", "Taran", "Vinod", "Alisha", "Bhavika", 
    "Chahna", "Damini", "Eesha", "Farah", "Gayatri", 
    "Himani", "Jyoti", "Karuna", "Laxmi", "Meenal", 
    "Neelima", "Ojasvi", "Padmini", "Quadirah", "Rupal", 
    "Shalini", "Tejal", "Urmila", "Vishwa", "Wilma", 
    "Yamini", "Zoya", "Anushka", "Sita", "Taruna", 
    "Naina", "Neelam", "Komal", "Nisha", "Ritika", 
    "Shobha", "Vijaya", "Amaya", "Bhavini", "Chandrika", 
    "Diksha", "Esha", "Falguni", "Gulshan", "Harini", 
    "Ida", "Juhi", "Kavya", "Lakshmi", "Malati", 
    "Nirmala", "Padma", "Rakhi", "Suman", "Vimla", 
    "Yogita", "Akshara", "Chaitali", "Dhruti", "Geetanjali", 
    "Harmoni", "Kanak", "Lavina", "Meghana", "Nalini", 
    "Padmavati", "Rupali", "Shreeja", "Tanvi", "Uma", 
    "Vaijanti", "Yamini", "Zohra", "Anvita", "Bhanvi", 
    "Chhavi", "Diya", "Eshita", "Gaurika", "Hema", 
    "Irsha", "Kashish", "Lavanya", "Mamata", "Nishtha", 
    "Pallavi", "Ruchi", "Suman", "Tina", "Urmila", 
    "Vijaya", "Yashvi", "Zeenat", "Aditi", "Anika", 
    "Bhagya", "Chhaya", "Dharini", "Ekta", "Gunjan", 
    "Himalaya", "Ikra", "Jaya", "Kavya", "Lalita", 
    "Manjari", "Naina", "Oorja", "Padma", "Ritika", 
    "Sejal", "Tanya", "Udita", "Vinita", "Yamini", 
    "Zara", "Aaravi", "Bhavya", "Chitra", "Deepali", 
    "Ekisha", "Fatima", "Geeta", "Hiral", "Ishta", 
    "Jaya", "Kanika", "Lavanya", "Meenal", "Nikita", 
    "Oorja", "Poonam", "Radhika", "Shreya", "Tanya", 
    "Urja", "Vaishali", "Yashasvi", "Zara", "Aditi", 
    "Ananya", "Anika", "Avantika", "Bhavna", "Chhavi", 
    "Deepa", "Eesha", "Gauri", "Hemlata", "Ishita", 
    "Kavita", "Kirti", "Lavanya", "Meera", "Neha", 
    "Nidhi", "Pooja", "Priya", "Riya", "Sanya", 
    "Sneha", "Tanvi", "Urvashi", "Vani", "Vidya"
]


haryana_places = [
    "Ambala", "Bhiwani", "Chandigarh", "Faridabad", "Fatehabad",
    "Gurgaon", "Hisar", "Jhajjar", "Jind", "Kaithal",
    "Karnal", "Mahendragarh", "Mewat", "Palwal", "Panchkula",
    "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat",
    "Yamunanagar", "Bahadurgarh", "Bilaspur", "Charkhi Dadri", "Dabwali",
    "Farukhnagar", "Gohana", "Hansi", "Hisar", "Isharwal",
    "Jaurasi", "Jind", "Kalanaur", "Kharar", "Khanpur",
    "Kharak", "Kharkhoda", "Kurukshetra", "Ladwa", "Loharu",
    "Mahendragarh", "Masani", "Mundhal Khurd", "Nahar", "Narnaund",
    "Nawada", "Nehar", "Palra", "Pehowa", "Rajaund",
    "Rania", "Ratia", "Rohtak", "Sadalpur", "Sahibabad",
    "Saha", "Samalkha", "Sankhol", "Shahzadpur", "Sohna",
    "Sonkh", "Sultanpur", "Taraori", "Thanesar", "Tohana",
    "Uklana", "Gharaunda", "Assandh", "Baraudi", "Barwala",
    "Bidhwan", "Bishanpur", "Bohar", "Brahmanwas", "Budhera",
    "Chhuchhura", "Chirawa", "Churu", "Dharuhera", "Dudhwa",
    "Fatehpur", "Gandhi Dham", "Ganaur", "Garhi Bolni", "Gharaunda",
    "Guhla", "Hussainpur", "Isharwal", "Jandli", "Jindal",
    "Kaithal", "Kalanaur", "Kanina", "Khanpur", "Kharkhoda",
    "Kharak", "Ladwa", "Madhuban", "Manda", "Mankera",
    "Nangal", "Naraingarh", "Narwana", "Nizampur", "Pehowa",
    "Pillar", "Pundri", "Rania", "Rohtak", "Sadhaura",
    "Saharanwas", "Salarpur", "Sarsa", "Sidhrawali", "Sikanderpur",
    "Sikandarpur", "Sonipat", "Sultanpur", "Suwalkheda", "Thana Ganga",
    "Tigaon", "Tiraha", "Uchana", "Ujhana", "Ujjain",
    "Umlana", "Uttar Pradesh", "Vijaypur", "Wazirabad", "Yamuna Nagar",
    "Abhay Pur", "Adampur", "Alipur", "Amin", "Anjanthali",
    "Bachhod", "Baghpat", "Bahror", "Baniyani", "Baragaon",
    "Bawana", "Bihari", "Bithori", "Chandresh", "Daulatpur",
    "Dhamtan", "Duggal", "Fatehpur", "Gaddi", "Gaggar",
    "Ganeshpur", "Ghari", "Gharuan", "Gohra", "Gulabgarh",
    "Harsaru", "Hathin", "Jabri", "Jharri", "Jharsa",
    "Jhundri", "Kaanjhera", "Kalyanpur", "Kandela", "Kaniyadh",
    "Kankra", "Karera", "Khanpur", "Kharak", "Kharkhoda",
    "Madhopur", "Malab", "Mangal", "Mohanpur", "Mora",
    "Murthal", "Nahar", "Nari", "Naya Gaon", "Neoli",
    "Nuh", "Palra", "Panchkula", "Pattikhera", "Pehowa",
    "Pukhraya", "Pundri", "Rajendra", "Ramgarh", "Rasulpur",
    "Sahibpur", "Salhawas", "Samsherpur", "Sanghera", "Saraswati",
    "Satyawadi", "Sidhpur", "Singhania", "Sirsa", "Tajpur",
    "Taraori", "Tiraha", "Tosham", "Ujhana", "Urswala"
]


def get_params():
    name = random.choice(["Dr. ", "Dr ", "DR ", "dr ", ""]) + random.choice(name_options)
    name = name.replace(" ", "+")
    ini = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")+random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
    name = random.choices([name, " ", ini], weights=[15, 1, 5], k = 1)[0]
    rank = random.randint(10000, 120000)
    posting = random.choice(["chc ", "CHC ", "PHC ", "Phc ", "GH ", "SDH ", ""]) + random.choice(haryana_places)
    posting = posting.replace(" ", "+")
    posting = random.choices([posting, " "], weights=[15, 1], k = 1)[0]
    cat = random.choices(["UR","UR+IP", "SC", "SC+IP", "SCD", "BCA", "BCA+IP", "BCB", "BCB+IP"], weights=[10,2,2, 1, 1, 4, 1, 3, 1], k = 1)[0]
    service = random.choices(["HCMS", "ESI"], weights=[10,1], k = 1)[0]
    pay_status = random.choices(["WITH+PAY", "WITHOUT+PAY", "NOT+ISSUED+TILL+NOW"], weights=[10,2,1], k = 1)[0]
    ts = int(time.time()*1000)
    return name, rank, posting, cat, service, pay_status, ts

while True:
    try:

        name, rank, posting, cat, service, pay_status, ts = get_params()
        formatted_time = time.strftime("%H:%M:%S", time.localtime(ts//1000))

        out = requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfi5B-kNoJe480GSJHfWRBWwKg-H9w5x9zD4GcOCDzcuj-j7A/formResponse",
            data=f'entry.945586746={name}&entry.169041868={rank}&entry.2110263961={posting}&entry.2040254798={cat}&entry.1718094845={service}&entry.2032804762={pay_status}&entry.2032804762_sentinel=&fvv=1&partialResponse=%5Bnull%2Cnull%2C%227837285864520324581%22%5D&pageHistory=0&fbzx=7837285864520324581&submissionTimestamp={ts}',
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "DNT": "1",
                "Origin": "https://docs.google.com",
                "Priority": "u=0, i",
                "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSfi5B-kNoJe480GSJHfWRBWwKg-H9w5x9zD4GcOCDzcuj-j7A/viewform",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "TE": "trailers",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": ""
            },
            cookies={},
            auth=(),
        )

        #with open("abc.html", "w") as f: f.write(out.text)
        
        if "The question has changed." in out.text: print(formatted_time, name, rank, posting, cat, service, pay_status, "Error!")
        else: print(formatted_time, name, rank, posting, cat, service, pay_status)
        #time.sleep(random.randint(0, 2))
    except:
        print("Some error!!!")