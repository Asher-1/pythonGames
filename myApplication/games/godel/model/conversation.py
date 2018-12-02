"""Model for a conversation system"""

import sqlite3
import os
import csv


class ConversationItem(object):
    """Represents an entry in a conversation"""

    def __init__(self, guid, person, order, state, displayed,
                 situation, provides, requires, conversation_text, present):
        """Initialise the item"""
        self.guid = guid
        self.person = person
        self.order = order
        self.state = state
        self.displayed = displayed
        self.situation = situation
        self.requires = requires if requires != [''] else []
        self.provides = provides if provides != [''] else []
        self.conversation_text = conversation_text
        self.present = present if present != [''] else []

    def __repr__(self):
        """Nice string representation"""
        return '<Conversation: guid:{0}, name:{1}, order:{2}, displayed:{4}, text:{3}'.format(
            self.guid, self.person, self.order, self.conversation_text, self.displayed,
        )


class ConversationSystem(object):
    """The model of a conversation system"""

    db_file = ['game', 'conversation.db']

    def __init__(self, db_file=None, recreate=False):
        """Initialise the conversation system"""
        #
        # Find the real filename
        filename = db_file if db_file else os.path.join(*self.db_file)
        #
        if recreate:
            self.deleteDb(filename)
        #
        self.db = self.connectToDb(filename)
        self.cur = self.db.cursor()

    def deleteDb(self, filename):
        """Delete the database file"""
        if os.path.isfile(filename):
            os.remove(filename)

    def connectToDb(self, filename):
        """Connect to the database - or create it if needed"""
        #
        # Do we need to create?
        create_tables = not os.path.isfile(filename)
        #
        # Connect
        db = sqlite3.connect(filename)
        db.row_factory = sqlite3.Row
        #
        # Create tables
        if create_tables:
            self.createTables(db)
        #
        return db

    def createTables(self, db):
        """Create the tables"""
        cur = db.cursor()
        cur.execute('''
          create table items (
            id INTEGER PRIMARY KEY,
            person TEXT,
            item_order INTEGER,
            state TEXT,
            displayed INTEGER,
            situation TEXT,
            provides TEXT,
            requires TEXT,
            conversation_text TEXT,
            present TEXT
          )
        ''')
        #
        cur.execute('''
          create table knowledge (
            item TEXT
          )
        ''')

    def closeConnection(self):
        """Close the database connection"""
        if self.db:
            self.cur = None
            self.db.close()
            self.db = None

    def addKnowledge(self, items):
        """Add items of knowledge"""
        knows_about = self.getKnowledge()
        for item in items:
            if item not in knows_about:
                self.cur.execute('insert into knowledge VALUES (?)', [item])
        #
        self.db.commit()

    def removeKnowledge(self, item):
        """Remove an item of knowledge"""
        self.cur.execute('delete from knowledge where item=?', [item])
        self.db.commit()

    def getKnowledge(self):
        """Return all the knowledge that we know about"""
        self.cur.execute('select * from knowledge')
        return [item['item'] for item in self.cur.fetchall()]

    def knowsAbout(self, items):
        """Return True if we know about all the items"""
        knows_about = self.getKnowledge()
        for item in items:
            if item not in knows_about:
                return False
        else:
            return True

    def addEntry(self, person, order, state, displayed, situation, provides=None, requires=None,
                 conversation_text='', present=None):
        """Add a conversation entry"""
        #
        # Get comma separated lists
        provides_string = '' if provides is None else ','.join(provides)
        requires_string = '' if requires is None else ','.join(requires)
        present_string = '' if not present else ','.join(present)
        #
        self.cur.execute('insert into items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         [None, person, order, state, displayed, situation,
                          provides_string, requires_string, conversation_text,
                          present_string])
        #
        self.db.commit()
        #
        self.cur.execute('select last_insert_rowid()')
        return self.cur.fetchone()[0]

    def getEntry(self, guid):
        """Return an entry by its guid"""
        self.cur.execute('select * from items where rowid = ?', [guid])
        return self.getItemFromRow(self.cur.fetchone())

    def getItemFromRow(self, row):
        """Return a conversation item from a row"""
        #
        # Make sure we at least had something
        if not row:
            return None
        #
        return ConversationItem(
            guid=row['id'],
            person=row['person'],
            order=row['item_order'],
            state=row['state'],
            displayed=row['displayed'] == 1,
            situation=row['situation'],
            provides=row['provides'].split(','),
            requires=row['requires'].split(','),
            conversation_text=row['conversation_text'],
            present=row['present'].split(','),
        )

    def getNext(self, person=None, situation=None, state=None):
        """Return the next conversation item to use for this situation"""
        where_clause = []
        where_variables = []
        for variable, name in [(person, 'person'), (situation, 'situation'), (state, 'state')]:
            if variable:
                where_clause.append('{0}=?'.format(name))
                where_variables.append(variable)
        #
        self.cur.execute('''
          select * from items
          where {0}
          and displayed=0
          ORDER BY item_order ASC
        '''.format(' AND '.join(where_clause)), where_variables)
        #
        # Filter down the results to make sure we have the knowledge that they require
        for row in self.cur.fetchall():
            item = self.getItemFromRow(row)
            if not item.requires or self.knowsAbout(item.requires):
                return item
        else:
            #
            # There weren't any items that we had all the information for
            return None

    def getAndUseNext(self, person=None, situation=None, state=None):
        """Return the next conversation item and use it up"""
        item = self.getNext(person, situation, state)
        #
        # If we got an item then set the displayed flag for it and generate the knowledge
        if item:
            self.cur.execute('update items set displayed=1 where id=?', [item.guid])
            self.addKnowledge(item.provides)
        #
        return item

    def loadFromFile(self, filename):
        """Load the data from a CSV file"""
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.addEntry(
                    person=row['Person'],
                    order=row['Order'],
                    state=row['State'],
                    displayed=False,
                    situation=row['Situation'],
                    provides=row['Provides'].split(','),
                    requires=row['Requires'].split(','),
                    conversation_text=row['Text'],
                    present=list(row['Present']),
                )

    def convertPresentToRequires(self, requires_string):
        """Convert all the present fields to a requirement for the people to be alive"""
        self.cur.execute('select id from items')
        for identity in self.cur.fetchall():
            guid = identity[0]
            item = self.getEntry(guid)
            extra_requires = [requires_string.format(name) for name in item.present]
            new_requires = item.requires + extra_requires
            new_requires_string = ','.join(new_requires)
            self.cur.execute('update items set requires=? where id=?', [new_requires_string, guid])
        #
        self.db.commit()