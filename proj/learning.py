class Dog: 
    species = "Canine" # Class variable

    def __init__(self, name , age):
        self.name = name
        self.age = age
    
    def __str__(self):
        return f"{self.name} is {self.age} years old."

dog1 = Dog("Buddy", 3)
dog2 = Dog("Charles", 5)   

print(dog1)
print(dog2)

dog1.name = "Max"  # Updates dog1 name
print(dog1)

Dog.species = "Feline"  # Updates the class variable

class Person:
    def __init__(self,name,age):
        self.__name = name
        self.__age = age

    # Getter 
    def get_age(self):
        return self.__age # Returns age
    
    # Setter
    def set_age(self,age):
        if age >= 0:
            self.__age = age # If age is a real one, it sets the new age, otherwise it returns an error
        else:
            print("no negative ages")

p = Person("Alice", 30)
p.set_age(35)        # Valid update
print(p.get_age())   # 35

p.set_age(-5)        # Invalid update
print(p.get_age())   # Still 35