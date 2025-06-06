#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <iomanip>
#include <map>

using namespace std;

class CryptoApp {
public:
    void run() {
        while (true) {
            printMenu();
            int choice;
            cin >> choice;

            if (choice == 1) calculateROI();
            else if (choice == 2) showExchanges();
            else if (choice == 3) showPriceChanges();
            else if (choice == 4) break;
            else cout << "Invalid option\n";
        }
    }

private:
    map<string, map<string, double>> cryptoData = {
        {"Bitcoin", {{"week", 5.2}, {"month", -3.1}, {"year", 120.5}}},
        {"Ethereum", {{"week", 7.8}, {"month", 12.3}, {"year", 85.2}}},
        {"Ripple", {{"week", -2.1}, {"month", -5.4}, {"year", 23.7}}},
        {"Litecoin", {{"week", 1.5}, {"month", 8.9}, {"year", 45.3}}},
        {"Cardano", {{"week", 3.7}, {"month", 15.6}, {"year", 210.8}}}
    };

    map<string, map<string, double>> exchangeData = {
        {"Binance", {{"BTC", 19345.32}, {"ETH", 1320.45}, {"24h_volume", 28.5}}},
        {"Coinbase", {{"BTC", 19340.12}, {"ETH", 1319.87}, {"24h_volume", 5.3}}},
        {"Kraken", {{"BTC", 19342.56}, {"ETH", 1321.03}, {"24h_volume", 3.1}}},
        {"FTX", {{"BTC", 19338.91}, {"ETH", 1320.12}, {"24h_volume", 2.5}}},
        {"KuCoin", {{"BTC", 19343.78}, {"ETH", 1320.67}, {"24h_volume", 1.8}}}
    };

    void printMenu() {
        cout << "\nCrypto Tracker\n";
        cout << "1. ROI Calculator\n";
        cout << "2. Exchange Information\n";
        cout << "3. Price Changes\n";
        cout << "4. Exit\n";
        cout << "Select option: ";
    }

    void calculateROI() {
        double investment, buyPrice, sellPrice;

        cout << "Initial Investment (USD): ";
        cin >> investment;

        cout << "Buy Price (USD per coin): ";
        cin >> buyPrice;

        cout << "Current/Sell Price (USD per coin): ";
        cin >> sellPrice;

        if (investment <= 0 || buyPrice <= 0 || sellPrice <= 0) {
            cout << "Error: Values must be positive\n";
            return;
        }

        double coins = investment / buyPrice;
        double finalValue = coins * sellPrice;
        double profit = finalValue - investment;
        double roi = (profit / investment) * 100;

        cout << fixed << setprecision(2);
        cout << "Final Value: $" << finalValue << "\n";
        cout << "Profit: $" << profit << "\n";
        cout << "ROI: " << roi << "%\n";
    }

    void showExchanges() {
        cout << "\nTop Cryptocurrency Exchanges (24h volume in $B):\n";
        for (const auto& exchange : exchangeData) {
            cout << exchange.first << ": $" << exchange.second.at("24h_volume") << "B\n";
            cout << "  BTC: $" << exchange.second.at("BTC") << "\n";
            cout << "  ETH: $" << exchange.second.at("ETH") << "\n\n";
        }
    }

    void showPriceChanges() {
        cout << "\nSelect cryptocurrency:\n";
        int i = 1;
        vector<string> cryptos;
        for (const auto& crypto : cryptoData) {
            cout << i << ". " << crypto.first << "\n";
            cryptos.push_back(crypto.first);
            i++;
        }

        int cryptoChoice;
        cout << "Choice: ";
        cin >> cryptoChoice;

        if (cryptoChoice < 1 || cryptoChoice > cryptos.size()) {
            cout << "Invalid choice\n";
            return;
        }

        string selectedCrypto = cryptos[cryptoChoice - 1];

        cout << "\nSelect period:\n";
        cout << "1. 1 week\n";
        cout << "2. 1 month\n";
        cout << "3. 1 year\n";

        int periodChoice;
        cout << "Choice: ";
        cin >> periodChoice;

        string period;
        if (periodChoice == 1) period = "week";
        else if (periodChoice == 2) period = "month";
        else if (periodChoice == 3) period = "year";
        else {
            cout << "Invalid choice\n";
            return;
        }

        double change = cryptoData[selectedCrypto][period];
        string trend = change >= 0 ? "up" : "down";

        cout << "\n" << selectedCrypto << " price change (" << period << "): ";
        cout << trend << " " << abs(change) << "%\n";

        drawSimpleChart(change);
    }

    void drawSimpleChart(double change) {
        cout << "\nPrice change chart:\n";
        int width = 20;
        int midpoint = width / 2;

        for (int i = 0; i < 10; i++) {
            for (int j = 0; j < width; j++) {
                if (j == midpoint) cout << "|";
                else if (i == 5 && j < midpoint && j > midpoint - abs(change) / 5) {
                    cout << (change > 0 ? "#" : "-");
                }
                else if (i == 5 && j > midpoint && j < midpoint + abs(change) / 5) {
                    cout << (change > 0 ? "#" : "-");
                }
                else cout << " ";
            }
            cout << "\n";
        }
        cout << (change > 0 ? "Price increase" : "Price decrease") << "\n";
    }
};

int main() {
    CryptoApp app;
    app.run();
    return 0;
}
