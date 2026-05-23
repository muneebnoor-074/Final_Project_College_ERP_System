# -*- coding: utf-8 -*-
"""
Created on Sun May 10 20:08:52 2026

@author: Muneeb Noor
"""
import time

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

MONTHS = {
    "january":   (19, "Capricorn",    "Aquarius"),
    "february":  (18, "Aquarius",     "Pisces"),    
    "march":     (20, "Pisces",       "Aries"),
    "april":     (19, "Aries",        "Taurus"),
    "may":       (20, "Taurus",       "Gemini"),
    "june":      (20, "Gemini",       "Cancer"),
    "july":      (22, "Cancer",       "Leo"),
    "august":    (22, "Leo",          "Virgo"),
    "september": (22, "Virgo",        "Libra"),
    "october":   (22, "Libra",        "Scorpio"),
    "november":  (21, "Scorpio",      "Sagittarius"),
    "december":  (21, "Sagittarius",  "Capricorn"),
}

MONTH_DAYS = {
    "january": 31, "february": 29, "march": 31, "april": 30,
    "may": 31, "june": 30, "july": 31, "august": 31,
    "september": 30, "october": 31, "november": 30, "december": 31
}

GOOD_HABITS = {
    "Aries":        ["Pioneering", "Courageous", "Enthusiastic", "Confident"],
    "Taurus":       ["Reliable", "Patient", "Thorough", "Loving", "Warmhearted"],
    "Gemini":       ["Versatile", "Adaptable", "Witty", "Communicative", "Logical"],
    "Cancer":       ["Sensitive", "Loving", "Intuitive", "Emotional", "Protective"],
    "Leo":          ["Generous", "Creative", "Broad-minded", "Expansive"],
    "Virgo":        ["Meticulous", "Reliable", "Modest", "Efficient", "Practical"],
    "Libra":        ["Peaceable", "Diplomatic", "Charming", "Fair"],
    "Scorpio":      ["Powerful", "Magnetic", "Exciting", "Passionate", "Sensitive"],
    "Sagittarius":  ["Straightforward", "Honest", "Intelligent"],
    "Capricorn":    ["Prudent", "Practical", "Patient", "Careful", "Disciplined"],
    "Aquarius":     ["Humanitarian", "Loyal", "Honest", "Unconventional", "Friendly"],
    "Pisces":       ["Sensitive", "Compassionate", "Imaginative", "Kind"],
}

BAD_HABITS = {
    "Aries":        ["Foolhardy", "Daredevil", "Impulsive", "Impatient"],
    "Taurus":       ["Possessive", "Jealous", "Resentful", "Indulgent", "Inflexible"],
    "Gemini":       ["Tense", "Nervous", "Cunning", "Inquisitive", "Superficial"],
    "Cancer":       ["Moody", "Changeable", "Touchy", "Overemotional", "Clinging"],
    "Leo":          ["Arrogant", "Interfering", "Bossy", "Dogmatic", "Intolerant"],
    "Virgo":        ["Fussy", "Perfectionist", "Worrier", "Overcritical", "Conservative"],
    "Libra":        ["Self-indulgent", "Gullible", "Easily-influenced", "Inertial"],
    "Scorpio":      ["Obsessive", "Resentful", "Compulsive"],
    "Sagittarius":  ["Restless", "Tactless", "Superficial", "Irresponsible"],
    "Capricorn":    ["Suspicious", "Miserly", "Pessimistic", "Fatalistic"],
    "Aquarius":     ["Perverse", "Unpredictable", "Unemotional", "Detnached"],
    "Pisces":       ["Escapist", "Vague", "Easily-led", "Impractical"],
}

def get_zodiac_sign(month: str, date: int) -> str:
    month = month.strip().lower()
    cutoff, first_sign, second_sign = MONTHS[month]
    return first_sign if date <= cutoff else second_sign


def print_traits(sign: str, trait_type: str) -> None:
    traits = GOOD_HABITS[sign] if trait_type == "good" else BAD_HABITS[sign]
    color = Colors.GREEN if trait_type == "good" else Colors.RED
    
    for i, trait in enumerate(traits, start=1):
        print(f"  {color}{i}. {trait}{Colors.RESET}")
        time.sleep(0.4)


def ask_yes_no(prompt: str) -> bool:
    return input(f"{Colors.YELLOW}{prompt}{Colors.RESET}").strip().lower() in ("yes", "y")


def get_valid_month() -> str:
    while True:
        month = input(f"{Colors.CYAN}Enter your birth month (e.g. January): {Colors.RESET}").strip().lower()
        if month in MONTHS:
            return month
        print(f"{Colors.RED}  '{month}' is not a valid month. Try again.{Colors.RESET}")


def get_valid_date(month: str) -> int:
    max_days = MONTH_DAYS[month]
    while True:
        try:
            date = int(input(f"{Colors.CYAN}Enter your birth date (1-{max_days}): {Colors.RESET}").strip())
            if 1 <= date <= max_days:
                return date
            print(f"{Colors.RED}  Please enter a valid day for {month.capitalize()} (1-{max_days}).{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}  That's not a valid number. Try again.{Colors.RESET}")


def print_banner():
    banner = f"""{Colors.MAGENTA}{Colors.BOLD}
     ===================================== 
           ZODIAC SIGN EXPLORER          
     ===================================== 
    {Colors.RESET}"""
    print(banner)

def main():
    print_banner()

    if not ask_yes_no("Do you want to start? (yes/no): "):
        print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}\n")
        return

    name = input(f"\n{Colors.CYAN}Enter your name: {Colors.RESET}").strip()
    print(f"\nHello, {Colors.BOLD}{name}{Colors.RESET}! Let's find your zodiac sign.\n")

    month = get_valid_month()
    date = get_valid_date(month) 

    sign = get_zodiac_sign(month, date)

    print(f"\nYour zodiac sign is: {Colors.BOLD}{Colors.MAGENTA}{sign.upper()}{Colors.RESET}\n")
    time.sleep(0.5)

    if ask_yes_no("Do you want to see your positive traits? (yes/no): "):
        print(f"\n{Colors.BOLD}{Colors.GREEN} Positive traits for {sign}: {Colors.RESET}")
        print_traits(sign, "good")
        time.sleep(0.5)

    if ask_yes_no("\nDo you want to see your negative traits? (yes/no): "):
        print(f"\n{Colors.BOLD}{Colors.RED} Negative traits for {sign}: {Colors.RESET}")
        print_traits(sign, "bad")

    print(f"\n{Colors.CYAN}Nice meeting you, {name}. May the stars be with you! Goodbye!{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Program interrupted by user. Goodbye!{Colors.RESET}")
