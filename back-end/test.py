from rapidfuzz import fuzz

title_1 = "The Substance"
title_2 = "Substance, The"
title_3 = "Wicked (NL)"
title_4 = "Wicked"

print("The Substance vs Substance, The:", fuzz.token_sort_ratio(title_1, title_2), "%")
print("Wicked (NL) vs Wicked:", fuzz.token_sort_ratio(title_3, title_4), "%")
