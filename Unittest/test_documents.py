import unittest
from documents_app import check_document_existance, get_doc_owner_name, get_all_doc_owners_names, remove_doc_from_shelf, add_new_shelf, append_doc_to_shelf, delete_doc

DOCUMENTS = [
    {"type": "passport", "number": "2207 876234", "name": "Василий Гупкин"},
    {"type": "invoice", "number": "11-2", "name": "Геннадий Покемонов"},
    {"type": "insurance", "number": "10006", "name": "Аристарх Павлов"}
]

DIRECTORIES = {
    '1': ['2207 876234', '11-2', '5455 028765'],
    '2': ['10006'],
    '3': []
}

class TestDocumentFunctions(unittest.TestCase):

    def setUp(self):
        self.documents = [doc.copy() for doc in DOCUMENTS]
        self.directories = {k: v[:] for k, v in DIRECTORIES.items()}

    def test_check_document_existance(self):
        self.assertTrue(check_document_existance(self.documents, "2207 876234"))
        self.assertFalse(check_document_existance(self.documents, "nonexistent"))

    def test_get_doc_owner_name(self):
        self.assertEqual(get_doc_owner_name(self.documents, "2207 876234"), "Василий Гупкин")
        self.assertIsNone(get_doc_owner_name(self.documents, "nonexistent"))

    def test_get_all_doc_owners_names(self):
        expected_names = {"Василий Гупкин", "Геннадий Покемонов", "Аристарх Павлов"}
        self.assertEqual(get_all_doc_owners_names(self.documents), expected_names)

    def test_remove_doc_from_shelf(self):
        self.assertTrue(remove_doc_from_shelf(self.directories, "2207 876234"))
        self.assertFalse("2207 876234" in self.directories['1'])
        self.assertFalse(remove_doc_from_shelf(self.directories, "nonexistent"))

    def test_add_new_shelf(self):
        self.assertTrue(add_new_shelf(self.directories, "4"))
        self.assertIn("4", self.directories)
        self.assertFalse(add_new_shelf(self.directories, "1"))

    def test_append_doc_to_shelf(self):
        self.assertTrue(append_doc_to_shelf(self.directories, "new_doc", "3"))
        self.assertIn("new_doc", self.directories["3"])
        self.assertTrue(append_doc_to_shelf(self.directories, "new_doc2", "5"))
        self.assertIn("5", self.directories)
        self.assertIn("new_doc2", self.directories["5"])

    def test_delete_doc(self):
      self.assertTrue(delete_doc(self.documents, self.directories, "2207 876234"))
      self.assertEqual(len(self.documents), 2)
      self.assertNotIn("2207 876234", self.directories.get("1", []))
      self.assertFalse(delete_doc(self.documents, self.directories, "nonexistent"))
      self.assertEqual(len(self.documents), 2)

if __name__ == '__main__':
    unittest.main()