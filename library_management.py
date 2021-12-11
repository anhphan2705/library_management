#Extracting information group
def read_file(directory):
    """
    Open file and read its content

    Param:
    - directory: directory of a file

    Return: 
    - a list that each value is one line of the txt
    """
    try:
        with open(directory) as file:
            text = file.readlines()
            for index in range(0, len(text)):
                word = text[index]
                if "\n" in word:
                    text[index] = word[:-1]
            return text
    except FileNotFoundError:
        print("File is not found")

def read_library_log(log):
    """
    Go through the library log to sort each command into a appropriate place
    - Borrow book:      B#<day>#<Student Name>#<Book name>#<days borrowed for>
    - Return book:      R#<day>#<Student Name>#<Book name>
    - Addition book:    A#<day>#<Book name>
    - Fine pay:         P#<day>#<student name>#<amount>
    
    Param:
    - log: the library log

    Return: 
    - borrow_log = a list of command lines regarding information of book being borrowed
    - return_log = a list of command lines regarding information of book being returned
    - addition_log = a list of command lines regarding information of book being added
    - fine_log = a list of comand lines regarding information of people being fined
    - day_available = an int that represent the amount of days the log is available
    """
    borrow_log = []
    return_log = []
    addition_log = []
    fine_log = []
    day_available = 0
    
    for line in log:
        function_type = line[:line.find("#")]
        if function_type == "B":
            borrow_log.append(line)
        elif function_type == "R":
            return_log.append(line)
        elif function_type == "A":
            addition_log.append(line)
        elif function_type == "P":
            fine_log.append(line)
        elif line.isdigit():
            day_available = int(line)
             
    return borrow_log, return_log, addition_log, fine_log, day_available

def extract_log_parts(log):
    """
    Extract each element out of the log by separating each value by # 
    - Format type "B": [[B] [day] [name] [book] [days borrowed for]]
    - Format type "R": [[R] [day] [name] [book]]
    - Format type "A": [[A] [day] [book]]
    - Format type "P": [[P] [day] [name]]
    
    Param:
    - log: a log that contains information needed to be extract separated by #
    
    Return: 
    - tuple: contain all information as a list with nested list
    """
    recs = []
    for line in log:
        recs.append(line.split('#'))
    
    return list(map(list, zip(*recs)))

def extract_data(log):
    """
    Extract data from log and put each type in the same list
    - Format: [[day], [name], [book], [duration]]
    
    Param:
    - log: the activity that it being logged

    Return: 
    - list: a list of activity that is sorted to the format above
    """
    return list(map(list, zip(*log)))

# General calendar function
def add_info(calendar, info):
    """
    Add information into the calendar in the appropriate day
    
    Param:
    - type_id: "S" = storage (id: 0) / B" = borrow (id: 1) / "R" = return (id: 2) / "A" = add (id: 3) / "P" = fine (id: 4)
    - info: list of information that need to be added
    
    Return:
    - calendar: a new calendar with added information
    """
    type_id_dict = {"S":0,
                   "B":1, 
                   "R":2,
                   "A":3,
                   "P":4}
    
    type_id = info[0][0]
    info.pop(0)
    data_location = type_id_dict.get(type_id)
    log_action = list(map(list, zip(*info)))
    
    for index in range(len(log_action)):
        day = int(log_action[index][0])
        data = calendar.get(day)
        data[data_location].append(log_action[index])
        calendar.update({day:data})
        
    return calendar

def update_storage(calendar, book_available, day):
    """
    Update book availability as a storage format into the calendar for a desired day
    
    Param:
    - calendar: the calendar that holds all activity
    - book_available: the storage list that contains all the available books' info

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data = calendar.get(day).copy()
    data[0] = book_available.copy()
    data[0][1] = data[0][1].copy()
    calendar.update({day:data})

    return calendar

#Borrow functions
def authorization_check(book_storage, book, duration):
    """
    Check if this borrow transaction is allowed.
    It checks for the duration of borrow regarding the restrict guideline and the quantity of available book
    
    Param:
    - book_storage: the available book list
    - book: the name of the book
    - day: the day of borrow
    - duration: days borrowed for

    Return: 
    - authorization: True/False that the transaction is allowed
    """  
    authorization = True
    for index in range(len(book_storage[0])):
        if (book_storage[0][index] == book):
            if book_storage[1][index] == 0:
                authorization = False
            if book_storage[2][index] == "TRUE":
                if duration > 7:
                    authorization = False
            if book_storage[2][index] == "FALSE":
                if duration > 28:
                    authorization = False
            break
    
    return authorization

def book_borrow(storage, book, duration):
    """
    This function ONLY work when the borrow request PASS the authorization_check. If it does, the transaction is allowed and decrease that book available quantity by 1.
    
    Param:
    - storage: the available book list
    - book: the name of the book
    - duration the duration of borrowing

    Return: [[books], [quantity], [restricted_type]]
    - storage_new: a new storage that has the quantity of the book borrowed decreased by 1
    """
    if authorization_check(storage, book, int(duration)):
        storage_new = storage.copy()
        storage_new[1] = storage_new[1].copy()
        for book_available_index in range(len(storage[0])):
            book_available = storage_new[0][book_available_index]
            if book_available == book:
                storage_new[1][book_available_index] = int(storage_new[1][book_available_index]) - 1
                break
        return storage_new
    else:
        return storage
  
def calendar_borrow_update(calendar, day):
    """
    Main function that process all borrow activity through each day of the calendar 
    by going through each borrow log of the day and call appropriate actions
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the desired day that will be processed

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data_previous = calendar.get(day-1).copy()
    data_current = calendar.get(day).copy()
    storage = data_previous[0].copy()
    if data_current[1] != []:
        borrow_log = data_current[1].copy()
        extracted_borrow_data = extract_data(borrow_log)
        books = extracted_borrow_data[2]
        durations = extracted_borrow_data[3]
        for index in range(len(books)):
                storage = book_borrow(storage, books[index], int(durations[index]))
                calendar = update_storage(calendar, storage, day) 
    else:
        calendar = update_storage(calendar, storage, day)
    
    return calendar

#Return functions
def book_return(storage, book):
    """
    This function is used to increase the quantity of book available in storage by 1.
    
    Param:
    - storage: the available book list
    - book: the name of the book

    Return: [[books], [quantity], [restricted_type]]
    - storage_new: a new storage that has the quantity of the book borrowed increase by 1
    """
    storage_new = storage.copy()
    storage_new[1] = storage_new[1].copy()
    for book_available_index in range(len(storage[0])):
        book_available = storage_new[0][book_available_index]
        if book_available == book:
            storage_new[1][book_available_index] = int(storage_new[1][book_available_index]) + 1
            break
    return storage_new

def calendar_return_update(calendar, day):
    """
    Main function that process all return activity through each day of the calendar 
    by going through each return log of the day and call appropriate actions
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the desired day that will be processed

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data_current = calendar.get(day).copy()
    storage = data_current[0].copy()
    if data_current[2] != []:
        return_log = data_current[2].copy()
        extracted_return_data = extract_data(return_log)
        books = extracted_return_data[2]
        for index in range(len(books)):
                storage = book_return(storage, books[index])
                calendar = update_storage(calendar, storage, day) 
    else:
        calendar = update_storage(calendar, storage, day)
    
    return calendar

#Main calendar activity processor
def calendar_activity_update(calendar):
    """
    Update the calendar completely by going through each activity each day to 
    process the book availability when borrowed, returned, added    
    
    Param:
    - calendar: the calendar that holds all activity

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log] ]}
    - calendar: a new calendar that holds all updated activity
    """
    days = list(calendar.keys())
    days.pop(0)
    for day in days:
        calendar = calendar_borrow_update(calendar, day)
        calendar  = calendar_return_update(calendar, day)
    
    return calendar

def calendar_generator(extracted_book_log, extracted_borrow_log, extracted_return_log, extracted_addition_log, extracted_fine_log, day_available):
    """
    Create a calendar that will add all the information from logs that are passed in with the day_available length.
    - Format: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log] ]}
    
    Param:
    - extracted_book_log = a list of book, quantity and restricted status of the book
    - extracted_borrow_log = a list of command lines regarding information of book being borrowed
    - extracted_return_log = a list of command lines regarding information of book being returned
    - extracted_addition_log = a list of command lines regarding information of book being added
    - extracted_fine_log = a list of comand lines regarding information of people being fined
    - day_available = an int that represent the amount of days the log is available
    
    Return:
    - calendar: a calendar with information
    """
    calendar = {day: [[] for element in range(5)] for day in range(day_available)}
    calendar = add_info(calendar, extracted_borrow_log)
    calendar = add_info(calendar, extracted_return_log)
    calendar = add_info(calendar, extracted_addition_log)
    calendar = add_info(calendar, extracted_fine_log)
    for day in calendar.keys():
        calendar = update_storage(calendar, extracted_book_log, day)

    return calendar

#Main part of the program
def main():
    #Read given information
    log_library = read_file("Final Project\library_management\librarylog.txt")
    log_book = read_file("Final Project\library_management\\booklist.txt")
    #Extracting information in to appropriate storing places
    extracted_book_log = extract_log_parts(log_book)
    log_book, log_return, log_addition, log_fine, day_available = read_library_log(log_library)
    extracted_borrow_log = extract_log_parts(log_book)
    extracted_return_log = extract_log_parts(log_return)
    extracted_addition_log = extract_log_parts(log_addition)
    extracted_fine_log = extract_log_parts(log_fine)
    #Calendar
    calendar = calendar_generator(extracted_book_log, extracted_borrow_log, extracted_return_log, extracted_addition_log, extracted_fine_log, day_available)
    calendar = calendar_activity_update(calendar)
    #print
    for key,value in calendar.items():
        print(key, value)

main()