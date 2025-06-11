#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <vector>
#include <algorithm>
#include <chrono>
#include <ctime>

namespace fs = std::filesystem;

void printHelp() {
    std::cout << "Консольная утилита для работы с файлами\n";
    std::cout << "Использование:\n";
    std::cout << "  fileutil [команда] [аргументы]\n\n";
    std::cout << "Команды:\n";
    std::cout << "  help - вывести эту справку\n";
    std::cout << "  copy <исходный файл> <целевой файл> - копировать файл\n";
    std::cout << "  delete <файл> - удалить файл\n";
    std::cout << "  info <файл> - показать информацию о файле\n";
    std::cout << "  list <директория> - список файлов в директории\n";
    std::cout << "  find <директория> <шаблон> - найти файлы по шаблону\n";
}

void copyFile(const std::string& source, const std::string& destination) {
    try {
        fs::copy_file(source, destination, fs::copy_options::overwrite_existing);
        std::cout << "Файл скопирован: " << source << " -> " << destination << "\n";
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Ошибка копирования: " << e.what() << "\n";
    }
}

void deleteFile(const std::string& filename) {
    try {
        if (fs::remove(filename)) {
            std::cout << "Файл удален: " << filename << "\n";
        } else {
            std::cerr << "Файл не найден: " << filename << "\n";
        }
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Ошибка удаления: " << e.what() << "\n";
    }
}

void fileInfo(const std::string& filename) {
    try {
        if (!fs::exists(filename)) {
            std::cerr << "Файл не найден: " << filename << "\n";
            return;
        }

        auto fileStatus = fs::status(filename);
        auto fileSize = fs::file_size(filename);
        auto lastWriteTime = fs::last_write_time(filename);

        auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
            lastWriteTime - fs::file_time_type::clock::now() + std::chrono::system_clock::now());
        std::time_t cftime = std::chrono::system_clock::to_time_t(sctp);

        std::cout << "Информация о файле: " << filename << "\n";
        std::cout << "Размер: " << fileSize << " байт\n";
        std::cout << "Тип: " << (fs::is_directory(fileStatus) ? "Директория" : "Файл") << "\n";
        std::cout << "Последнее изменение: " << std::asctime(std::localtime(&cftime));
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Ошибка получения информации: " << e.what() << "\n";
    }
}

void listFiles(const std::string& directory) {
    try {
        std::cout << "Содержимое директории " << directory << ":\n";
        for (const auto& entry : fs::directory_iterator(directory)) {
            std::cout << "  " << entry.path().filename().string();
            if (fs::is_directory(entry.status())) {
                std::cout << " [DIR]";
            } else {
                std::cout << " (" << fs::file_size(entry.path()) << " байт)";
            }
            std::cout << "\n";
        }
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Ошибка чтения директории: " << e.what() << "\n";
    }
}

void findFiles(const std::string& directory, const std::string& pattern) {
    try {
        std::cout << "Поиск файлов по шаблону '" << pattern << "' в " << directory << ":\n";
        for (const auto& entry : fs::recursive_directory_iterator(directory)) {
            if (!fs::is_directory(entry.status())) {
                std::string filename = entry.path().filename().string();
                if (filename.find(pattern) != std::string::npos) {
                    std::cout << "  " << entry.path().string() << "\n";
                }
            }
        }
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Ошибка поиска: " << e.what() << "\n";
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printHelp();
        return 1;
    }

    std::string command = argv[1];

    if (command == "help") {
        printHelp();
    } else if (command == "copy" && argc == 4) {
        copyFile(argv[2], argv[3]);
    } else if (command == "delete" && argc == 3) {
        deleteFile(argv[2]);
    } else if (command == "info" && argc == 3) {
        fileInfo(argv[2]);
    } else if (command == "list" && argc == 3) {
        listFiles(argv[2]);
    } else if (command == "find" && argc == 4) {
        findFiles(argv[2], argv[3]);
    } else {
        std::cerr << "Неверная команда или количество аргументов\n";
        printHelp();
        return 1;
    }

    return 0;
}
