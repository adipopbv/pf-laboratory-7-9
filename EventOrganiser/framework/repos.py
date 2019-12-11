from EventOrganiser.domain.entities import Command, Person, Event, Attendance
from EventOrganiser.domain.exceptions import *
from EventOrganiser.domain.fields import Address, Date
from EventOrganiser.framework.json_tools import JsonFileSaver


class Repo:

    _items: list
    @property
    def items(self):
        return self._items
    @items.setter
    def items(self, value):
        self._items = value

    # ------------------

    def __init__(self, items: list):
        self.items = items

    def index_of(self, entity):
        try:
            return self.items.index(entity)
        except:
            raise NotInRepoException


class ModifiableRepo(Repo):

    def add(self, entity):
        self.items.append(entity)

    def delete(self, entity):
        try:
            self.items.remove(entity)
        except:
            raise NotInRepoException

    def modify(self, old_entity, new_entity):
        self.items[self.index_of(old_entity)] = new_entity


class FileRepo(Repo, JsonFileSaver):

    def __init__(self, file_name: str, items: list):
        Repo.__init__(self, items)
        JsonFileSaver.__init__(self, file_name)
        self.load_from_file()

    def save_to_file(self):
        file = open(self.file_name, "w")
        try:
            data_list = [item.to_json() for item in self.items]
            data = self.json.dumps(data_list, indent=4)
            file.write(data)
            file.close()
        except Exception as ex:
            file.close()
            raise Exception(ex)


class CommandRepo(Repo):

    def __init__(self, commands: list):
        super().__init__(commands)


class CommandFileRepo(FileRepo, CommandRepo):

    def __init__(self, file_name: str):
        FileRepo.__init__(self, file_name, [])
        self.load_from_file()

    def load_from_file(self):
        file = open(self.file_name, "r")
        try:
            file_string = file.read()
            data = self.json.loads(file_string)

            commands = []
            for data_command in data:
                keys = []
                for data_key in data_command["keys"]:
                    keys.append(data_key)
                commands.append(Command(data_command["function"], data_command["description"], keys))

            self.items = commands
            file.close()
        except Exception as ex:
            file.close()
            raise Exception(ex)


class ModifiableFileRepo(ModifiableRepo, JsonFileSaver):

    def __init__(self, file_name: str, items: list):
        ModifiableRepo.__init__(self, items)
        JsonFileSaver.__init__(self, file_name)
        self.load_from_file()

    def add(self, entity):
        super().add(entity)
        self.save_to_file()

    def delete(self, entity):
        super().delete(entity)
        self.save_to_file()

    def modify(self, old_entity, new_entity):
        super().modify(old_entity, new_entity)
        self.save_to_file()

    def save_to_file(self):
        file = open(self.file_name, "w")
        try:
            data_list = [item.to_json() for item in self.items]
            data = self.json.dumps(data_list, indent=4)
            file.write(data)
            file.close()
        except Exception as ex:
            file.close()
            raise Exception(ex)


class PersonRepo(ModifiableRepo):

    def get_person_with_field_value(self, field, value):
        if field != "address":
            if len(self.items) == 0:
                raise EmptyRepoException
            for person in self.items:
                try:
                    if getattr(person, field) == value:
                        return person
                except:
                    try:
                        if getattr(person.address, field) == value:
                            return person
                    except:
                        pass
        raise NoFieldWithValueException


class PersonFileRepo(ModifiableFileRepo, PersonRepo):

    def __init__(self, file_name: str, items: list):
        ModifiableFileRepo.__init__(self, file_name, items)
        self.load_from_file()

    def load_from_file(self):
        file = open(self.file_name, "r")
        try:
            file_string = file.read()
            data = self.json.loads(file_string)

            persons = []
            for data_person in data:
                persons.append(Person(
                    data_person["id"],
                    data_person["name"],
                    Address(
                        data_person["address"]["city"],
                        data_person["address"]["street"],
                        data_person["address"]["number"]
                    )
                ))

            self.items = persons
            file.close()
        except Exception as ex:
            file.close()
            raise Exception(ex)


class EventRepo(ModifiableRepo):

    def get_event_with_field_value(self, field, value):
        if field != "date":
            if len(self.items) == 0:
                raise EmptyRepoException
            for event in self.items:
                try:
                    if getattr(event, field) == value:
                        return event
                except:
                    try:
                        if getattr(event.date, field) == value:
                            return event
                    except:
                        pass
        raise NoFieldWithValueException


class EventFileRepo(ModifiableFileRepo, EventRepo):

    def __init__(self, file_name: str, items: list):
        ModifiableFileRepo.__init__(self, file_name, items)
        self.load_from_file()

    def load_from_file(self):
        file = open(self.file_name, "r")
        try:
            file_string = file.read()
            data = self.json.loads(file_string)

            events = []
            for data_event in data:
                events.append(Event(
                    data_event["id"],
                    Date(
                        data_event["date"]["day"],
                        data_event["date"]["month"],
                        data_event["date"]["year"]
                    ),
                    data_event["duration"],
                    data_event["description"]
                ))

            self.items = events
            file.close()
        except Exception as ex:
            file.close()
            raise Exception(ex)


class AttendanceRepo(ModifiableRepo):

    def get_free_id(self):
        return len(self.items)

    def get_attendances_with_person(self, person: Person):
        attendances = []
        if len(self.items) == 0:
            raise EmptyRepoException
        for attendance in self.items:
            try:
                if attendance.person == person:
                    attendances.append(attendance)
            except:
                raise NotPersonException
        return attendances


class AttendanceFileRepo(ModifiableFileRepo, AttendanceRepo):

    def __init__(self, file_name: str, items: list):
        ModifiableFileRepo.__init__(self, file_name, items)
        self.load_from_file()

    def load_from_json(self):
        file = open(self.file_name, "r")
        try:
            file_string = file.read()
            data = self.json.loads(file_string)

            attendances = []
            for data_attendance in data:
                attendances.append(Attendance(
                    data_attendance["id"],
                    Person(
                        data_attendance["person"]["id"],
                        data_attendance["person"]["name"],
                        Address(
                            data_attendance["person"]["address"]["city"],
                            data_attendance["person"]["address"]["street"],
                            data_attendance["person"]["address"]["number"]
                        )
                    ),
                    Event(
                        data_attendance["event"]["id"],
                        Date(
                            data_attendance["event"]["date"]["day"],
                            data_attendance["event"]["date"]["month"],
                            data_attendance["event"]["date"]["year"]
                        ),
                        data_attendance["event"]["duration"],
                        data_attendance["event"]["description"]
                    )
                ))

            self.items = attendances
            file.close()
        except Exception as ex:
            file.close()
            raise Exception(ex)
