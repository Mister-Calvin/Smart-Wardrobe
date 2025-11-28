from models import Base, Wardrobe

class DataManager():

    def create_item(self, name):
        new_item = Wardrobe(name=name)
        try:
            Base.session.add(new_item)
            Base.session.commit()
            return True
        except Exception as e:
            Base.session.rollback()
            print(f"failed to create item:{e}")
            return False
        finally:
            Base.session.close()

