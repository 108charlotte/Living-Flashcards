ratings = {
    "again": 1, 
    "hard": 2, 
    "good": 3, 
    "easy": 4
}

# need to update intervals of cards based on ratings

def to_next_review_to_display_string(to_next_review_num): 
    if to_next_review_num < 0.15: 
        return "< 15 mins"
    elif to_next_review_num < 1: 
        return str(to_next_review_num * 100) + " min(s)"
    elif to_next_review_num < 31: 
        return str(to_next_review_num) + " day(s)"
    elif to_next_review_num < 365: 
        # gets number of months (rounded)
        return str(to_next_review_num // 28) + " month(s)"
    else: 
        return str(to_next_review_num // 365) + " year(s)"