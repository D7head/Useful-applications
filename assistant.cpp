#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>
#include <ctime>
#include <chrono>
#include <thread>
#include <map>
#include <sstream>
#include <fstream>

using namespace std;

struct Task {
    string description;
    bool completed;
    string dueDate;
};

struct Note {
    string title;
    string content;
    string date;
};

struct Contact {
    string name;
    string phone;
    string email;
};

vector<Task> tasks;
vector<Note> notes;
vector<Contact> contacts;
map<string, double> exchangeRates = {
    {"USD", 1.0},
    {"EUR", 0.85},
    {"GBP", 0.72},
    {"JPY", 110.25},
    {"RUB", 75.50}
};

void addTask() {
    Task newTask;
    cout << "Введите описание задачи: ";
    cin.ignore();
    getline(cin, newTask.description);
    cout << "Введите срок выполнения (ДД.ММ.ГГГГ): ";
    cin >> newTask.dueDate;
    newTask.completed = false;
    tasks.push_back(newTask);
    cout << "Задача добавлена!\n";
}

void showTasks() {
    if (tasks.empty()) {
        cout << "Список задач пуст.\n";
        return;
    }
    
    cout << "Список задач:\n";
    for (size_t i = 0; i < tasks.size(); ++i) {
        cout << i + 1 << ". " << (tasks[i].completed ? "[X] " : "[ ] ")
             << tasks[i].description << " (до: " << tasks[i].dueDate << ")\n";
    }
}

void completeTask() {
    showTasks();
    if (tasks.empty()) return;
    
    int index;
    cout << "Введите номер задачи для отметки о выполнении: ";
    cin >> index;
    
    if (index > 0 && index <= static_cast<int>(tasks.size())) {
        tasks[index - 1].completed = true;
        cout << "Задача отмечена как выполненная!\n";
    } else {
        cout << "Неверный номер задачи.\n";
    }
}

void addNote() {
    Note newNote;
    cout << "Введите заголовок заметки: ";
    cin.ignore();
    getline(cin, newNote.title);
    cout << "Введите содержание заметки: ";
    getline(cin, newNote.content);
    
    time_t now = time(0);
    tm* ltm = localtime(&now);
    stringstream date;
    date << 1900 + ltm->tm_year << "-" << 1 + ltm->tm_mon << "-" << ltm->tm_mday;
    newNote.date = date.str();
    
    notes.push_back(newNote);
    cout << "Заметка добавлена!\n";
}

void showNotes() {
    if (notes.empty()) {
        cout << "Нет сохраненных заметок.\n";
        return;
    }
    
    cout << "Ваши заметки:\n";
    for (size_t i = 0; i < notes.size(); ++i) {
        cout << "=== " << notes[i].title << " (" << notes[i].date << ") ===\n";
        cout << notes[i].content << "\n\n";
    }
}

void addContact() {
    Contact newContact;
    cout << "Введите имя: ";
    cin.ignore();
    getline(cin, newContact.name);
    cout << "Введите телефон: ";
    getline(cin, newContact.phone);
    cout << "Введите email: ";
    getline(cin, newContact.email);
    
    contacts.push_back(newContact);
    cout << "Контакт добавлен!\n";
}

void showContacts() {
    if (contacts.empty()) {
        cout << "Список контактов пуст.\n";
        return;
    }
    
    cout << "Ваши контакты:\n";
    for (size_t i = 0; i < contacts.size(); ++i) {
        cout << i + 1 << ". " << contacts[i].name << "\n";
        cout << "   Телефон: " << contacts[i].phone << "\n";
        cout << "   Email: " << contacts[i].email << "\n\n";
    }
}

void pomodoroTimer() {
    int workMinutes, breakMinutes;
    cout << "Введите продолжительность работы (в минутах): ";
    cin >> workMinutes;
    cout << "Введите продолжительность перерыва (в минутах): ";
    cin >> breakMinutes;
    
    cout << "Pomodoro таймер запущен! Работайте...\n";
    this_thread::sleep_for(chrono::minutes(workMinutes));
    cout << "\aВремя работы закончилось! Сделайте перерыв.\n";
    this_thread::sleep_for(chrono::minutes(breakMinutes));
    cout << "\aПерерыв закончился! Возвращайтесь к работе.\n";
}

void currencyConverter() {
    cout << "Доступные валюты: ";
    for (const auto& rate : exchangeRates) {
        cout << rate.first << " ";
    }
    cout << "\n";
    
    string from, to;
    double amount;
    
    cout << "Введите исходную валюту: ";
    cin >> from;
    transform(from.begin(), from.end(), from.begin(), ::toupper);
    
    cout << "Введите целевую валюту: ";
    cin >> to;
    transform(to.begin(), to.end(), to.begin(), ::toupper);
    
    cout << "Введите сумму: ";
    cin >> amount;
    
    if (exchangeRates.find(from) == exchangeRates.end() ||
        exchangeRates.find(to) == exchangeRates.end()) {
        cout << "Неизвестная валюта.\n";
        return;
    }
    
    double result = (amount / exchangeRates[from]) * exchangeRates[to];
    cout << fixed << setprecision(2);
    cout << amount << " " << from << " = " << result << " " << to << "\n";
}

void saveData() {
    ofstream taskFile("tasks.txt"), noteFile("notes.txt"), contactFile("contacts.txt");
    
    for (const auto& task : tasks) {
        taskFile << task.description << "\n" << task.completed << "\n" << task.dueDate << "\n";
    }
    
    for (const auto& note : notes) {
        noteFile << note.title << "\n" << note.content << "\n" << note.date << "\n";
    }
    
    for (const auto& contact : contacts) {
        contactFile << contact.name << "\n" << contact.phone << "\n" << contact.email << "\n";
    }
    
    cout << "Данные сохранены.\n";
}

void loadData() {
    ifstream taskFile("tasks.txt"), noteFile("notes.txt"), contactFile("contacts.txt");
    string line;
    
    tasks.clear();
    while (getline(taskFile, line)) {
        Task task;
        task.description = line;
        getline(taskFile, line);
        task.completed = (line == "1");
        getline(taskFile, line);
        task.dueDate = line;
        tasks.push_back(task);
    }
    
    notes.clear();
    while (getline(noteFile, line)) {
        Note note;
        note.title = line;
        getline(noteFile, line);
        note.content = line;
        getline(noteFile, line);
        note.date = line;
        notes.push_back(note);
    }
    
    contacts.clear();
    while (getline(contactFile, line)) {
        Contact contact;
        contact.name = line;
        getline(contactFile, line);
        contact.phone = line;
        getline(contactFile, line);
        contact.email = line;
        contacts.push_back(contact);
    }
    
    cout << "Данные загружены.\n";
}

void showMenu() {
    cout << "\n=== Органайзер ===\n";
    cout << "1. Управление задачами\n";
    cout << "2. Заметки\n";
    cout << "3. Контакты\n";
    cout << "4. Pomodoro таймер\n";
    cout << "5. Конвертер валют\n";
    cout << "6. Сохранить данные\n";
    cout << "7. Загрузить данные\n";
    cout << "0. Выход\n";
    cout << "Выберите действие: ";
}

void taskMenu() {
    int choice;
    do {
        cout << "\n=== Управление задачами ===\n";
        cout << "1. Добавить задачу\n";
        cout << "2. Показать задачи\n";
        cout << "3. Отметить задачу как выполненную\n";
        cout << "0. Назад\n";
        cout << "Выберите действие: ";
        cin >> choice;
        
        switch (choice) {
            case 1: addTask(); break;
            case 2: showTasks(); break;
            case 3: completeTask(); break;
        }
    } while (choice != 0);
}

void noteMenu() {
    int choice;
    do {
        cout << "\n=== Заметки ===\n";
        cout << "1. Добавить заметку\n";
        cout << "2. Показать заметки\n";
        cout << "0. Назад\n";
        cout << "Выберите действие: ";
        cin >> choice;
        
        switch (choice) {
            case 1: addNote(); break;
            case 2: showNotes(); break;
        }
    } while (choice != 0);
}

void contactMenu() {
    int choice;
    do {
        cout << "\n=== Контакты ===\n";
        cout << "1. Добавить контакт\n";
        cout << "2. Показать контакты\n";
        cout << "0. Назад\n";
        cout << "Выберите действие: ";
        cin >> choice;
        
        switch (choice) {
            case 1: addContact(); break;
            case 2: showContacts(); break;
        }
    } while (choice != 0);
}

int main() {
    setlocale(LC_ALL, "Russian");
    
    int choice;
    do {
        showMenu();
        cin >> choice;
        
        switch (choice) {
            case 1: taskMenu(); break;
            case 2: noteMenu(); break;
            case 3: contactMenu(); break;
            case 4: pomodoroTimer(); break;
            case 5: currencyConverter(); break;
            case 6: saveData(); break;
            case 7: loadData(); break;
        }
    } while (choice != 0);
    
    cout << "До свидания!\n";
    return 0;
}
