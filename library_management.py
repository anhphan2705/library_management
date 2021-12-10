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
    - tuplle: contain all information as a list with nested list
    """
    recs = []
    for line in log:
        recs.append(line.split('#'))
    
    return list(map(list, zip(*recs)))

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

def update_storage(calendar, day, log_book):
    
    data = calendar.get(day)
    data[0] = log_book
    calendar.update({day:data})
    
    return calendar

# def update_storage(calendar, day, log_book):
#     if day == 0:
#         data = calendar.get(day)
#     else:
#         data = calendar.get(day-1)
#     data[0] = log_book.copy()
#     data[0][1] = data[0][1].copy()
#     calendar.update({day:data})

#     return calendar
        
def extract_data(log):
    day = []
    name = []
    book = []
    duration = []
    for action in log:
        day.append(int(action[0]))
        name.append(action[1])
        book.append(action[2])
        if len(action) > 3:
            duration.append(int(action[3]))
        
    return day, name, book, duration

def authorization_check(log_book, book, duration):
    """
    Check if this borrow transaction is allowed.
    It checks for the duration of borrow regarding the restrict guideline and the quantity of available book
    
    Param:
    - log_book: the available book list
    - book: the name of the book
    - day: the day of borrow
    - duration: days borrowed for

    Return: 
    - authorization: True/False that the transaction is allowed
    """  
    authorization = True
    for index in range(len(log_book[0])):
        if (log_book[0][index] == book):
            if log_book[1][index] == 0:
                authorization = False
            if log_book[2][index] == "TRUE":
                if duration > 7:
                    authorization = False
            if log_book[2][index] == "FALSE":
                if duration > 28:
                    authorization = False
            break
    
    return authorization

def borrow_book(log_book, book):

    for index in range(len(log_book[0])):
        book_in_storage = log_book[0][index]
        if (book_in_storage == book):
            quantity = int(log_book[1][index])
            log_book[1][index] = quantity - 1
            break

    return log_book  

def return_book(log_book, book):
    
    for index in range(len(log_book[0])):
        book_in_storage = log_book[0][index]
        if (book_in_storage == book):
            quantity = int(log_book[1][index])
            log_book[1][index] = quantity + 1
            break
        
    return log_book

def calendar_borrow_availability(calendar, up_to_day):
    
    for day in range(up_to_day):
        data = calendar.get(day)
        book_availability = data[0]
        borrow_log = data[1]
        days, names, books, durations = extract_data(borrow_log)

        if borrow_log != []:
            for index in range(len(books)):
                if authorization_check(book_availability, books[index], durations[index]):
                    book_availability = borrow_book(book_availability, books[index])
                    print(book_availability)
                    calendar = update_storage(calendar, days[index], book_availability) 
                    
    return calendar 

def calendar_return_availability(calendar, up_to_day):
    for day in range(up_to_day):
        data = calendar.get(day)
        book_availability = data[0]
        return_log = data[2]
        days, names, books, durations = extract_data(return_log)

        if return_log != []:
            for index in range(len(books)):
                book_availability = return_book(book_availability, books[index])
                print(book_availability)
                calendar = update_storage(calendar, days[index], book_availability) 
                    
    return calendar 

def calendar_live_update(calendar, up_to_day):
    
    for day in range(up_to_day):
        calendar = calendar_borrow_availability(calendar, day)
        calendar = calendar_return_availability(calendar, day)
        
    return calendar

def calendar_generator(extracted_book_log, extracted_borrow_log, extracted_return_log, extracted_addition_log, extracted_fine_log, day_available):
    """
    Create a calendar that will add all the information from logs that are passed in with the day_available length.
    - Format: {day : [ [storage] [borrow_log] [return_log] [addition_log] [fine_log] ]}
    
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
    #Create a new calendar
    calendar = {day: [[] for element in range(5)] for day in range(day_available)}
    for day in range(day_available):
        calendar = update_storage(calendar, day, extracted_book_log)
    calendar = add_info(calendar, extracted_borrow_log)
    calendar = add_info(calendar, extracted_return_log)
    calendar = add_info(calendar, extracted_addition_log)
    calendar = add_info(calendar, extracted_fine_log)

    return calendar
    
def main():
    #Read given information
    log_library = read_file("Final Project\\librarylog.txt")
    log_book = read_file("Final Project\\booklist.txt")
    #Extracting information in to appropriate storing places
    extracted_book_log = extract_log_parts(log_book)
    log_book, log_return, log_addition, log_fine, day_available = read_library_log(log_library)
    extracted_borrow_log = extract_log_parts(log_book)
    extracted_return_log = extract_log_parts(log_return)
    extracted_addition_log = extract_log_parts(log_addition)
    extracted_fine_log = extract_log_parts(log_fine)
    #Calendar
    calendar = calendar_generator(extracted_book_log, extracted_borrow_log, extracted_return_log, extracted_addition_log, extracted_fine_log, day_available)
    for day in range(day_available):
        calendar = calendar_live_update(calendar, day)
    #print
    for key,value in calendar.items():
        print(key, value)

main()