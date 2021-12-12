#Extracting information group
from os import name


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

    Return: [[day], [name], [book], [duration]]
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
    
    if info != []:
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

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data = calendar.get(day).copy()
    data[0] = book_available.copy()
    data[0][1] = data[0][1].copy()
    calendar.update({day:data})

    return calendar

def get_storage(calendar, day):
    """
    Get storage information
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the day in the calendar

    Return: [[books], [quantity], [restricted_type]]
    - storage: book availability
    """
    data = calendar.get(day).copy()
    storage = data[0].copy()
    
    return storage

def get_log_fine(calendar, day):
    """
    Get log fine information
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the day in the calendar

    Return: [[[day], [student}, [amount_fine_paying]]]
    - log_fine: the log that keep track of how much student owe 
    """
    data = calendar.get(day).copy()
    storage = data[4].copy()
    
    return storage

def add_book_tracking_format(calendar):
    
    format = [[] for element in range(3)]
    for day in list(calendar.keys()):
        data = calendar.get(day).copy()
        data[5] = data[5].copy()
        data[5] = format.copy()
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

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
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

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
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

#Add book functions
def book_add(storage, book):
    """
    This function is used to add new book or increase the book available quantity by 1
    
    Param:
    - storage: the available book list
    - book: the name of the book

    Return: [[books], [quantity], [restricted_type]]
    - storage_new: a new storage that has the quantity of the new book or existing book increase by 1
    """
    storage_new = storage.copy()
    storage_new[0] = storage_new[0].copy()
    storage_new[1] = storage_new[1].copy()
    storage_new[2] = storage_new[2].copy()
    is_exist_book = False
    for book_available_index in range(len(storage[0])):
        book_available = storage_new[0][book_available_index]
        if book_available == book:
            storage_new[1][book_available_index] = int(storage_new[1][book_available_index]) + 1
            is_exist_book = True
            break
    if not is_exist_book:
        storage_new[0].append(book) 
        storage_new[1].append("1")   
        storage_new[2].append("FALSE")     
     
    return storage_new
    
def calendar_add_update(calendar, day):
    """
    Main function that process all adding activity through each day of the calendar 
    by going through each adding log of the day and call appropriate actions
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the desired day that will be processed

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data_current = calendar.get(day).copy()
    storage = data_current[0].copy()
    if data_current[3] != []:
        add_log = data_current[3].copy()
        extracted_add_data = extract_data(add_log)
        books = extracted_add_data[1]
        for index in range(len(books)):
                storage = book_add(storage, books[index])
                calendar = update_storage(calendar, storage, day) 
    else:
        calendar = update_storage(calendar, storage, day)
    
    return calendar

#Late tracker        
def late_return_tracker(day, extracted_borrow_log, extracted_return_log):
    """
    Track all borrow and return transaction to determine late returner. Any violation will be added to a list.
    
    Param:
    - day: the desired day that will be processed
    - extracted_borrow_log: Format type "B": [[B] [day] [name] [book] [days borrowed for]]
    - extracted_return_log: Format type "R": [[R] [day] [name] [book]]

    Return: [ [student], [book], [late_day_need_to_pay] ]
    - late_tracking_log: a list that contains all the late return students's info
    """
    late_tracking_log = [[] for elements in range(3)]
    for borrow_index in range(len(extracted_borrow_log[0])):
        day_borrow = int(extracted_borrow_log[0][borrow_index])
        name_borrow = extracted_borrow_log[1][borrow_index]
        books_borrow = extracted_borrow_log[2][borrow_index]
        duration_borrow_requested = int(extracted_borrow_log[3][borrow_index])
        
        if day_borrow < day:
            for return_index in range(len(extracted_return_log[0])):
                day_return = int(extracted_return_log[0][return_index])
                name_return = extracted_return_log[1][return_index]
                books_return = extracted_return_log[2][return_index]
                if day_return <= day:
                    if (name_borrow == name_return) and (books_borrow == books_return):
                        day_return_expected = day_borrow + duration_borrow_requested
                        if day_return_expected < day_return:
                            late_days = day_return - day_return_expected
                            late_tracking_log[0].append(name_borrow)
                            late_tracking_log[1].append(books_borrow)
                            late_tracking_log[2].append(late_days)
                        break
    
    return late_tracking_log

def late_return_update(calendar, day, late_tracking_log):
    """
    Main function that process all late return through each day of the calendar 
    by going through each borrow and return log of up until the day of and call appropriate actions
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the desired day that will be processed
    - late_tracking_log: the log that contains late returner's info

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data_current = calendar.get(day).copy()
    data_current[5] = data_current[5].copy()
    data_current[5] = late_tracking_log
    calendar.update({day:data_current})
    
    return calendar

#Fine functions
def book_fine(storage, late_tracking_log):
    """
    Track all fine for late returner. Any violation will be added to a dictionary.
    
    Param:
    - storage: the list of book available. Format: [[books], [quantity], [restricted_type]]
    - late_tracking_log: late return students's info. Format: [ [student], [book], [late_day_need_to_pay] ]

    Return: {student: fine_amount}
    - fine_tracker: a dictionary contains student names and the fine they have to pay
    """
    fine_tracker = {}
    
    for index in range(len(late_tracking_log[0])):
        late_student = late_tracking_log[0][index]
        late_book = late_tracking_log[1][index]
        late_day = late_tracking_log[2][index]
        fee_per_day = 2
        for book_index in range(len(storage[0])):
            book = storage[0][book_index]
            restricted_type = storage[2][book_index]
            if late_book == book:
                if restricted_type == "TRUE":
                    fee_per_day = 5
                break
        fine_total = late_day * fee_per_day
        fine_tracker.update({late_student: fine_total})
        
    return fine_tracker

def fine_payment(log_fine, fine_tracker, day):
    """
    This function is used to detect payment in activity log. It will record the student and the payment and subtract it from the owe money. If the money goes to 0 it will delete it from the fine_tracker    
    
    Param:
    - log_fine: the list of payment. Format: [[[day], [student}, [amount_fine_paying]]]
    - fine_tracker: a dictionary contains student names and the fine they have to pay. Format: {student: fine_amount}
    - day: the day that it is being executed

    Return: {student: fine_amount}
    - fine_tracker: a dictionary contains student names and the fine left they have to pay
    """
    if log_fine != []:
        for transaction in log_fine:
            name_log = transaction[1]
            money_paid_log = int(transaction[2])
            money_owe = int(fine_tracker.get(name_log))
            money_left = money_owe - money_paid_log
            if money_left > 0:
                fine_tracker.update({name_log: money_left})
            else:
                fine_tracker.pop(name_log)
        
    return fine_tracker

def money_paid(late_tracking_log, fine_tracker, day):
    """
    This function detects the amount of money student pay.
    
    Param:
    - late_tracking_log: a list that contains all the late return students's info. Format: [ [student], [book], [late_day_need_to_pay] ]
    - fine_tracker: a dictionary contains student names and the fine they have to pay. Format: {student: fine_amount}
    - day: the day that need to be processed

    Return: {student: fine_amount}
    - late_tracking_log: a list that contains all the late return students's info. Format: [ [student], [book], [late_day_need_to_pay] ]
    """
    for index in range(len(late_tracking_log[0])):
        name = late_tracking_log[0][index]
        if name not in list(fine_tracker.keys()):
            late_tracking_log[0].pop(index)
            late_tracking_log[1].pop(index)
            late_tracking_log[2].pop(index)
            
    return late_tracking_log

def fine_processor(storage, late_tracking_log, log_fine, day):
    """
    This function is process fines and late return. It calls appropriate action for each transaction.
    
    Param:
    - late_tracking_log: a list that contains all the late return students's info. Format: [ [student], [book], [late_day_need_to_pay] ]
    - log_fine: the list of payment. Format: [[[day], [student}, [amount_fine_paying]]]
    - fine_tracker: a dictionary contains student names and the fine they have to pay. Format: {student: fine_amount}
    - day: the day that need to be processed

    Return: {student: fine_amount}
    - fine_tracker: a dictionary contains student names and the fine left they have to pay
    - late_tracking_log: a list that contains all the late return students's info. Format: [ [student], [book], [late_day_need_to_pay] ]
    """
    fine_tracker = book_fine(storage, late_tracking_log)
    fine_tracker = fine_payment(log_fine, fine_tracker, day)
    late_tracking_log = money_paid(late_tracking_log, fine_tracker, day)
    
    return fine_tracker, late_tracking_log

def fine_update(calendar, day, fine_tracker):
    """
    Keep track of how much money people owe the library
    by going through each payment and late day log up until the day of and call appropriate actions
    
    Param:
    - calendar: the calendar that holds all activity
    - day: the desired day that will be processed
    - fine_tracker: a dictionary contains student names and the fine left they have to pay

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    - calendar: a new calendar that holds all updated activity
    """
    data_current = calendar.get(day).copy()
    data_current[6] = data_current[6].copy()
    data_current[6] = fine_tracker
    calendar.update({day:data_current})
    
    return calendar
    
#Main calendar activity processor
def calendar_generator(extracted_book_log, extracted_borrow_log, extracted_return_log, extracted_addition_log, extracted_fine_log, day_available):
    """
    Create a calendar that will add all the information from logs that are passed in with the day_available length.
    - Format: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    
    Param:
    - extracted_book_log = a list of book, quantity and restricted status of the book
    - extracted_borrow_log = a list of command lines regarding information of book being borrowed
    - extracted_return_log = a list of command lines regarding information of book being returned
    - extracted_addition_log = a list of command lines regarding information of book being added
    - extracted_fine_log = a list of comand lines regarding information of people being fined
    - day_available = an int that represent the amount of days the log is available
    
    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    - calendar: a calendar with information
    """
    calendar = {day: [[] for element in range(7)] for day in range(day_available)}
    calendar = add_info(calendar, extracted_borrow_log)
    calendar = add_info(calendar, extracted_return_log)
    calendar = add_info(calendar, extracted_addition_log)
    calendar = add_info(calendar, extracted_fine_log)
    calendar = add_book_tracking_format(calendar)
    for day in calendar.keys():
        calendar = update_storage(calendar, extracted_book_log, day)

    return calendar

def calendar_activity_update(calendar, extracted_borrow_log, extracted_return_log):
    """
    Update the calendar completely by going through each activity each day to 
    process the book availability when borrowed, returned, added    
    
    Param:
    - calendar: the calendar that holds all activity

    Return: {day : [ [storage], [borrow_log], [return_log], [addition_log], [fine_log], [late_tracking] ]}
    - calendar: a new calendar that holds all updated activity
    """
    days = list(calendar.keys())
    days.pop(0)
    for day in days:
        calendar = calendar_borrow_update(calendar, day)
        calendar  = calendar_return_update(calendar, day)
        calendar = calendar_add_update(calendar, day)
        late_tracking_log = late_return_tracker(day, extracted_borrow_log, extracted_return_log)
        #recheck late_tracking_log
        calendar = late_return_update(calendar, day, late_tracking_log)
        storage = get_storage(calendar, day)
        log_fine = get_log_fine(calendar, day)
        fine_tracker, late_tracking_log = fine_processor(storage, late_tracking_log, log_fine, day)
        calendar = fine_update(calendar, day, fine_tracker)
        
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
    calendar = calendar_activity_update(calendar, extracted_borrow_log, extracted_return_log)
    #print
    for key,value in calendar.items():
        print(key, value)

main()