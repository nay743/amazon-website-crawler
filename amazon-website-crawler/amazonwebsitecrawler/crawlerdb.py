"""
Created on Feb 23, 2014

@author: nay

This class is used only within the crawler.py module as an
implementation of a crawler database.
"""

import Queue

class ProductDb:
    """This class implements a queue of elements of the form:
        (PRODUCT_ID, URL).
    """
    def __init__(self):
        self.ids_visited = set()
        self.url_queue = Queue.Queue(maxsize=0)

    def enqueue(self, url_data):
        """Adds an element to the database queue."""
        self.url_queue.put(url_data)

    def dequeue(self):
        """"Returns the next element (FIFO) in the database.
            Checks if the next element has not been visited before.
        """
        (product_id, url) = self.url_queue.get()
        while not self.empty() and self.already_crawled(product_id):
            (product_id, url) = self.url_queue.get()
        if self.empty() and self.already_crawled(product_id):
            return
        self.ids_visited.add(product_id)
        return (product_id, url)

    def already_crawled(self, product_id):
        """"Checks if the product_id belongs to a visited url."""
        return product_id in self.ids_visited

    def empty(self):
        """Checks if the database is empty."""
        return self.url_queue.empty()

    def urls_visited(self):
        """Returns the number of visited urls."""
        return len(self.ids_visited)


def main():
    """This function tests the ProductDb class"""

    # create a ProductDB database
    product_db = ProductDb()

    # enqueue some elements
    product_db.enqueue(('B00E1A1SP6',
            'http://www.amazon.com/Nintendo-3DS-XL-Black/dp/B00E1A1SP6'))
    product_db.enqueue(('B003O6E800',
            'http://www.amazon.com/Pok%C3%A9mon-Y-nintendo-3ds/dp/B0053B66KE'))
    product_db.enqueue(('B00E1A1SP6',
            'http://www.amazon.com/Nintendo-3DS-XL-Black/dp/B00E1A1SP6'))

    # print elements in database
    while not product_db.empty():
        print product_db.dequeue()

if __name__ == '__main__':
    main()
