from models import Base, Wardrobe, session

class DataManager():

    def create_item(self, name, category):
        new_item = Wardrobe(
            name=name,
            category=category
        )
        try:
            session.add(new_item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"failed to create item:{e}")
            return False
        finally:
            session.close()




if __name__ == '__main__':
    manager = DataManager()
    item = manager.create_item("Mein erster Test","warm")
    print(item)