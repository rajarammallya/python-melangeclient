# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import itertools


class TemplateTestHelper:

    def assertTableEquals(self, expected_row_maps, actual_contents):

        actual_lines = [line for line in actual_contents.splitlines() if line]
        actual_cells = [line.split("\t") for line in actual_lines]

        self.assertColumnCellWidthsAreEqual(actual_cells)

        actual_header = actual_lines.pop(0)
        self.assertHeader(expected_row_maps[0].keys(), actual_header)

        def cells_to_map(cells_in_a_line):
            return dict((key.strip(), cell.strip()) for key, cell
                        in itertools.izip(actual_cells[0], cells_in_a_line))

        actual_row_maps = [cells_to_map(cells_in_a_line) for cells_in_a_line
                           in actual_cells[1:]]

        self.assertUnorderedEqual(expected_row_maps, actual_row_maps)

    def assertColumnCellWidthsAreEqual(self, cells):
        cell_lengths = lambda lst: map(lambda cell: len(cell), lst)
        for column_values in zip(*cells):
            self.assertElementsAreSame(cell_lengths(column_values),
                                       "column with first element '%s' has "
                                       "dissimilar widths" % column_values[0])

    def assertElementsAreSame(self, lst, error_msg="List elements differ"):
        self.assertEqual(len(set(lst)), 1, error_msg)

    def assertHeader(self, expected_header_columns, actual_header):
        actual_header_columns = [header_column.strip() for header_column
                                 in actual_header.split("\t")]
        self.assertUnorderedEqual(expected_header_columns,
                                  actual_header_columns)
