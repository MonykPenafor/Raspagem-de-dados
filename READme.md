# Flashcard Generator - Web Scraping Project

## 📚 Overview

This project is a web scraping tool designed to automate the process of extracting flashcard data from a language learning website, [IKnowJP!](https://iknow.jp/content/japanese), and saving it into a database. The data includes vocabulary, translations, example sentences, pronunciation, and other relevant details. 

The extracted data integrates seamlessly with another project, [Flashcard Generator](https://github.com/MonykPenafor/Flashcard_Generator), which organizes and generates the final flashcards for language learning. Check out that repository to see how this data is utilized in practice.  

### Features

- Scrapes vocabulary details (source word, translation, pronunciation, and usage examples).
- Converts proficiency levels to standardized CEFR levels.
- Saves the data directly into a SQL Server database.
- Logs errors and saves failed items to a JSON file for troubleshooting. Check the failed items [here](https://github.com/MonykPenafor/Raspagem-de-dados/blob/main/failed_items.json). 

## 🛠️ Technologies Used

- **Python** (Core scripting language)
- **Selenium WebDriver** (Web scraping automation)
- **SQL Server** (Database)
- **pyodbc** (Database connection library)
- **Logging Module** (Error and process logging)

For additional context, the repository includes HTML reference files, which showcase the relevant sections of the website used for scraping data.


## 📋 Setup Instructions

### Prerequisites

- Python 3.8+
- Google Chrome and [ChromeDriver](https://sites.google.com/chromium.org/driver/) installed
- SQL Server with the specified database and table structure
- Necessary Python libraries (see requirements)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/flashcard-generator.git
   cd flashcard-generator

## 🗂️ Repository Contents
- scraper.py: Main script for scraping and saving data.
- failed_items.json: Log of failed items for troubleshooting.
- HTML Reference Files: Examples of website structure used during scraping.

## 🌟 Additional Information
### Error Handling:
Errors encountered during scraping are logged, and failed items are saved to a JSON file for easy review and reprocessing.

### Database Integration:
The script is optimized for SQL Server but can be adapted for other relational databases by modifying the connection settings in the code.

## 🚀 Related Projects
[Flashcard Generator](https://github.com/MonykPenafor/Flashcard_Generator): Uses the data from this project to generate language learning flashcards.