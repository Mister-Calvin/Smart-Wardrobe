from models import Wardrobe, Session

class DataManager():

    def get_all_items(self):
        session = Session()
        try:
            return session.query(Wardrobe).all()
        finally:
            session.close()

    def get_item_by_id(self, id):
        session = Session()
        try:
            return session.query(Wardrobe).filter(Wardrobe.id == id).first()
        finally:
            session.close()

    def create_item(self, name, description, color, condition, type, score):
        session = Session()
        new_item = Wardrobe(
            name=name,
            description=description,
            color=color,
            condition=condition,
            type=type,
            score=score,
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

    def delete_item(self, id):
        session = Session()
        try:
            item = session.query(Wardrobe).filter(Wardrobe.id == id).first()
            if item:
                session.delete(item)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"failed to delete item:{e}")
            return False
        finally:
            session.close()

    def delete_all_items(self):
        session = Session()
        try:
            session.query(Wardrobe).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"failed to delete all items:{e}")
            return False
        finally:
            session.close()

    def update_item(self, id, name, description, color, condition, type, score):
        session = Session()
        try:
            item = session.query(Wardrobe).filter(Wardrobe.id == id).first()
            if item:
                item.name = name
                item.description = description
                item.color = color
                item.condition = condition
                item.type = type
                item.score = score

                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"failed to update item:{e}")
            return False
        finally:
            session.close()
