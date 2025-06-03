#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <ctime>
#include <algorithm>
#include <limits>
#include <string>
#include <locale>

using namespace std;

struct Transaction {
    time_t date;
    double amount;
    string category;
    string description;
    bool isIncome;
};

class FinanceManager {
private:
    vector<Transaction> transactions;
    string dataFile = "transactions.dat";

    string formatDate(time_t date) {
        char buffer[80];
        tm timeInfo;
        localtime_s(&timeInfo, &date);
        strftime(buffer, sizeof(buffer), "%d.%m.%Y %H:%M", &timeInfo);
        return string(buffer);
    }

    void saveToFile() {
        ofstream outFile(dataFile, ios::binary);
        if (!outFile) {
            cerr << "Ошибка открытия файла для записи!" << endl;
            return;
        }

        for (const auto& t : transactions) {
            outFile.write(reinterpret_cast<const char*>(&t.date), sizeof(t.date));
            outFile.write(reinterpret_cast<const char*>(&t.amount), sizeof(t.amount));

            size_t categorySize = t.category.size();
            outFile.write(reinterpret_cast<const char*>(&categorySize), sizeof(categorySize));
            outFile.write(t.category.c_str(), categorySize);

            size_t descSize = t.description.size();
            outFile.write(reinterpret_cast<const char*>(&descSize), sizeof(descSize));
            outFile.write(t.description.c_str(), descSize);

            outFile.write(reinterpret_cast<const char*>(&t.isIncome), sizeof(t.isIncome));
        }

        outFile.close();
    }

    void loadFromFile() {
        ifstream inFile(dataFile, ios::binary);
        if (!inFile) {
            return;
        }

        transactions.clear();
        Transaction t;

        while (inFile.read(reinterpret_cast<char*>(&t.date), sizeof(t.date))) {
            inFile.read(reinterpret_cast<char*>(&t.amount), sizeof(t.amount));

            size_t categorySize;
            inFile.read(reinterpret_cast<char*>(&categorySize), sizeof(categorySize));
            t.category.resize(categorySize);
            inFile.read(&t.category[0], categorySize);

            size_t descSize;
            inFile.read(reinterpret_cast<char*>(&descSize), sizeof(descSize));
            t.description.resize(descSize);
            inFile.read(&t.description[0], descSize);

            inFile.read(reinterpret_cast<char*>(&t.isIncome), sizeof(t.isIncome));

            transactions.push_back(t);
        }

        inFile.close();
    }

public:
    FinanceManager() {
        loadFromFile();
    }

    ~FinanceManager() {
        saveToFile();
    }

    void addTransaction() {
        Transaction t;
        char choice;

        cout << "Это доход или расход? (д/р): ";
        cin >> choice;
        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        t.isIncome = (tolower(choice) == 'д');

        cout << "Введите сумму: ";
        while (!(cin >> t.amount)) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "Неверный ввод. Пожалуйста, введите число: ";
        }
        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        cout << "Введите категорию: ";
        getline(cin, t.category);

        cout << "Введите описание: ";
        getline(cin, t.description);

        t.date = time(nullptr);

        transactions.push_back(t);
        cout << "Транзакция успешно добавлена!" << endl;
    }

    void viewTransactions() {
        if (transactions.empty()) {
            cout << "Нет транзакций для отображения." << endl;
            return;
        }

        cout << "\nСписок всех транзакций:" << endl;
        cout << string(80, '-') << endl;
        cout << setw(20) << left << "Дата"
            << setw(10) << "Тип"
            << setw(15) << "Категория"
            << setw(12) << "Сумма"
            << "Описание" << endl;
        cout << string(80, '-') << endl;

        for (const auto& t : transactions) {
            cout << setw(20) << left << formatDate(t.date)
                << setw(10) << (t.isIncome ? "Доход" : "Расход")
                << setw(15) << t.category
                << setw(12) << fixed << setprecision(2) << t.amount
                << t.description << endl;
        }
        cout << string(80, '-') << endl;
    }

    void showSummary() {
        double totalIncome = 0;
        double totalExpense = 0;

        for (const auto& t : transactions) {
            if (t.isIncome) {
                totalIncome += t.amount;
            }
            else {
                totalExpense += t.amount;
            }
        }

        double balance = totalIncome - totalExpense;

        cout << "\nФинансовая сводка:" << endl;
        cout << string(30, '=') << endl;
        cout << "Общий доход: " << fixed << setprecision(2) << totalIncome << " руб." << endl;
        cout << "Общий расход: " << fixed << setprecision(2) << totalExpense << " руб." << endl;
        cout << string(30, '-') << endl;
        cout << "Баланс: " << fixed << setprecision(2) << balance << " руб." << endl;
        cout << string(30, '=') << endl;
    }

    void analyzeByCategory() {
        if (transactions.empty()) {
            cout << "Нет транзакций для анализа." << endl;
            return;
        }

        vector<string> categories;
        vector<double> incomeByCat;
        vector<double> expenseByCat;

        for (const auto& t : transactions) {
            if (find(categories.begin(), categories.end(), t.category) == categories.end()) {
                categories.push_back(t.category);
                incomeByCat.push_back(0);
                expenseByCat.push_back(0);
            }
        }

        for (const auto& t : transactions) {
            auto it = find(categories.begin(), categories.end(), t.category);
            if (it != categories.end()) {
                size_t index = distance(categories.begin(), it);
                if (t.isIncome) {
                    incomeByCat[index] += t.amount;
                }
                else {
                    expenseByCat[index] += t.amount;
                }
            }
        }

        cout << "\nАнализ по категориям:" << endl;
        cout << string(60, '=') << endl;
        cout << setw(20) << left << "Категория"
            << setw(15) << "Доход"
            << setw(15) << "Расход"
            << "Баланс" << endl;
        cout << string(60, '-') << endl;

        for (size_t i = 0; i < categories.size(); ++i) {
            double balance = incomeByCat[i] - expenseByCat[i];
            cout << setw(20) << left << categories[i]
                << setw(15) << fixed << setprecision(2) << incomeByCat[i] << " руб."
                    << setw(15) << expenseByCat[i] << " руб."
                    << fixed << setprecision(2) << balance << " руб." << endl;
        }
        cout << string(60, '=') << endl;
    }
};

void displayMenu() {
    cout << "\n=== Личный финансовый менеджер ===" << endl;
    cout << "1. Добавить транзакцию" << endl;
    cout << "2. Просмотреть все транзакции" << endl;
    cout << "3. Финансовая сводка" << endl;
    cout << "4. Анализ по категориям" << endl;
    cout << "5. Выход" << endl;
    cout << "Выберите действие: ";
}

int main() {
    setlocale(LC_ALL, "Russian");

    FinanceManager manager;
    int choice;

    do {
        displayMenu();
        cin >> choice;
        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        switch (choice) {
        case 1:
            manager.addTransaction();
            break;
        case 2:
            manager.viewTransactions();
            break;
        case 3:
            manager.showSummary();
            break;
        case 4:
            manager.analyzeByCategory();
            break;
        case 5:
            cout << "Выход из программы..." << endl;
            break;
        default:
            cout << "Неверный выбор. Пожалуйста, введите число от 1 до 5." << endl;
        }
    } while (choice != 5);

    return 0;
}
