# Your classes and functions here

class Enemy:

    enemies = []

    def __init__(self, hitpoints, damage):
        self.hitpoints = hitpoints
        self.damage = damage

        # Add instance to list
        Enemy.enemies.append(self)

    def __repr__(self):
        return f"Enemy(hitpoints = {self.hitpoints}, damage = {self.damage})"

    def take_hit(self, damage):
        self.hitpoints -= damage

        if self.hitpoints <= 0:
            # Remove once hp = 0
            if self in Enemy.enemies:
                Enemy.enemies.remove(self)
            return True
        return False

    def shoot(self, player):
        player.take_hit(self.damage)
        # If dead, returns True
        return player.hitpoints <= 0

class Player:
    def __init__(self, hitpoints, damage, nth=None):
        self.hitpoints = hitpoints
        self.damage = damage
        self.nth = nth
        self.shot_counter = 0

    def __repr__(self):
        return f"Player(hitpoints = {self.hitpoints}, damage = {self.damage})"

    def take_hit(self, damage):
        self.hitpoints -= damage
        return self.hitpoints <= 0

    def calc_dmg(self):
        self.shot_counter += 1

        # If no number, do nothing
        if self.nth is None:
            return self.damage

        # If shot = nth number, double
        if self.shot_counter % self.nth == 0:
            return self.damage * 2

        return self.damage

    def shoot_5_times(self):
        shots = 0

        while shots < 5 and Enemy.enemies:

            target = Enemy.enemies[0]
            dmg = self.calc_dmg()  # Fetch what damage the shot does
            target.take_hit(dmg)  # Deal damage

            shots += 1
        return len(Enemy.enemies) == 0  # Returns True if all are dead

def duel(player):
    while True:
        if Enemy.enemies:  # If there are enemies, shoot
            player.shoot_5_times()

        if not Enemy.enemies:
            print("The player won!")
            return

        # Each enemy shoots once
        for enemy in Enemy.enemies[:]:  # Copy list to avoid errors
            enemy.shoot(player)

            # If player dies, enemy win
            if player.hitpoints <= 0:
                print("The enemies won!")
                return

# Your script is in here (this makes sure it only runs if you run the specific file)
if __name__ == "__main__":

    p = Player(50, 10)

    Enemy(15, 15)
    Enemy(20, 15)
    Enemy(10, 15)
    Enemy(20, 15)

    duel(p)

    print("\nFinal state:")
    print(p)
    print("Enemies:", Enemy.enemies)
