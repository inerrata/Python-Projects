def fill_unique(lst, partial=None):
    # Partial stores the solution
    if partial is None:
        partial = []

    # Base case; if length of partial is longer than list return 
    remaining = lst[len(partial):]
    if not remaining:
        return partial

    # Split it so it can be evaluated index by index
    head, *tail = remaining

    if head != 0:  # When head is non-zero
        # Keep number, add to sol
        return fill_unique(lst, partial + [head])
    else:
        # Find smallest pos int which hasn't been used
        # Combines all used numbers and all non-zero numbers still in the remaining list
        used = set(partial + [x for x in remaining if x != 0])
        n = 1
        while n in used:
            n += 1
        return fill_unique(lst, partial + [n])

if __name__ == "__main__":
    lst = [3, 0, 0, 1]
    print(fill_unique(lst))  # [3, 2, 4, 1]

    lst2 = [0, 0, 1, 0]
    prefilled = [2, 3]
    print(fill_unique(lst2, prefilled))  # [2, 3, 1, 4]