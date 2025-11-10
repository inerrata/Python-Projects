# ---------------
# Pokemon and Trainer classes
# ---------------

class Pokemon:
    def __init__(self, name, level):
        self.__name = name  # Use __ to prevent it from being accessed unless strictly done
        self.__level = level
        self.__moves = set()  # Use a set to prevent duplicates when appending

    def add_move(self, move):
        self.__moves.add(move)

    def __repr__(self):
        return f"{self.__name} (Level: {self.__level}| Moves: {self.__moves})"

class Trainer:
    def __init__(self, name, owned):
        self.__name = name
        self.__pokemons = owned

    def __repr__(self):
        return f"{self.__name} pokemons: {self.__pokemons}"


# ---------------
# Script
# ---------------


# Mapping
def add_pokemon(pokemon_mapping, name, pokemon_id, level):
    
    # Check if it exists
    if pokemon_id in pokemon_mapping:
        print(f"Error: Pokemon ID {pokemon_id} already exists!")
        return

    # Adding pokemon
    pokemon_mapping[pokemon_id] = Pokemon(name, level)


def add_move(pokemon_mapping, unique_moves, pokemon_id, move):
    # Check if pokemon exists
    if pokemon_id not in pokemon_mapping:
        print(f"Error: Pokemon ID {pokemon_id} not found!")
        return

    pokemon = pokemon_mapping[pokemon_id]

    # Add move both to pokemon and unique move set list
    pokemon.add_move(move)
    unique_moves.add(move)
    
    # Print moveset
    print(unique_moves)

def add_trainer(trainer_mapping, trainer_name, trainer_id, pokemon_mapping, pokemon_ids):
    if trainer_id in trainer_mapping:
        print(f"Error: Trainer ID {trainer_id} already exists!")
        return

    for i in pokemon_ids:
        if i not in pokemon_mapping:  # For each index in pokemon_mapping, if pokemon at index i doesnt exist 
            print(f"Pokemon ID {i} not found!")
            return

    owned_pokemon = [pokemon_mapping[i] for i in pokemon_ids]
    trainer_mapping[trainer_id] = Trainer(trainer_name, owned_pokemon)
    
    
def strongest_pokemon(pokemon_mapping):
    max_level = -1  # Start at a negative level since it is possible for a Pokemon to be level 0
    strongest = None
    
    # Loop through all Pokemon
    for i in pokemon_mapping.values():
        if i._Pokemon__level > max_level:  
            max_level = i._Pokemon__level
            strongest = i  # If Pokemon at index i has higher max level, set strongest at this index
    
    return strongest

def battle(trainer1, trainer2):
    
    score1 = 0
    score2 = 0
    
    # Fetch list of pokemon per trainer
    pokemons1 = trainer1._Trainer__pokemons
    pokemons2 = trainer2._Trainer__pokemons
    
    # Max number of rounds
    rounds = min(len(pokemons1), len(pokemons2))
    
    # Fetch level of pokemon at index i for both trainers
    for i in range(rounds):
        level1 = pokemons1[i]._Pokemon__level
        level2 = pokemons2[i]._Pokemon__level
        
        # Pokemon from Trainer 1 has to strictly be higher otherwise Trainer 2 will get a point
        if level1 > level2:
            score1 += 1
        else:
            score2 += 1
            
    if score1 >= score2:
        print(f"{trainer1._Trainer__name} won the battle!")
    else:
        print(f"{trainer2._Trainer__name} won the battle!")
    
if __name__ == "__main__":
    
    # Data Structure init
    pokemons = {}
    trainers = {}
    unique_moves = set()
    
    # Add Pokemon
    add_pokemon(pokemons, "Pikachu", 1, 5)
    add_pokemon(pokemons, "Bulbasaur", 2, 8)
    add_pokemon(pokemons, "Charmander", 3, 5)
    add_pokemon(pokemons, "Squirtle", 4, 6)
    
    # Add Moves
    add_move(pokemons, unique_moves, 1, "Thunder Shock")
    add_move(pokemons, unique_moves, 1, "Quick Attack")
    add_move(pokemons, unique_moves, 2, "Vine Whip")
    add_move(pokemons, unique_moves, 2, "Tackle")
    add_move(pokemons, unique_moves, 3, "Ember")
    add_move(pokemons, unique_moves, 3, "Scratch")
    add_move(pokemons, unique_moves, 4, "Water Gun")
    add_move(pokemons, unique_moves, 4, "Bubble")
    
    # Add Trainers
    add_trainer(trainers, "Ash", 1, pokemons, [1, 2])
    add_trainer(trainers, "Brock", 2, pokemons, [3, 4])
    
    # Print Pokemon
    for i, p in pokemons.items():  # use .items() to print both the id and the pokemon itself
        print(f"ID {i}: {p}")
    
    # Print Trainer
    for k, t in trainers.items():
        print(f"ID {k}: {t}")
    
    # Print Unique Moves
    print(unique_moves)
    
    # Strongest Pokemon
    strongest = strongest_pokemon(pokemons)
    print(strongest)

    # Battle
    # Run battle without printing None
    battle(trainers[1], trainers[2])
