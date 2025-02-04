#!/usr/bin/env python3
###############################################################################
#
# Copyright 2006 - 2021, Tomas Babej, Paul Beckingham, Federico Hernandez.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://www.opensource.org/licenses/mit-license.php
#
###############################################################################

import sys
import os
import unittest
import re

# Ensure python finds the local simpletap module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from basetest import Task, TestCase


class ContextManagementTest(TestCase):
    def setUp(self):
        self.t = Task()

    def test_context_define_confirmation(self):
        """With confirmation active, prompt if context filter matches no tasks"""
        self.t.config("confirmation", "on")

        code, out, err = self.t.runError(
            "context define work project:Work", input="y\nn\n"
        )
        self.assertIn("The filter 'project:Work' matches 0 pending tasks.", out)
        self.assertNotIn("Context 'work' defined", out)

        # Assert the config contains context definition
        self.assertNotIn("context.work=project:Work\n", self.t.taskrc_content)

    def test_context_define(self):
        """Test simple context definition."""
        code, out, err = self.t("context define work project:Work", input="y\ny\nn\n")
        self.assertIn("Context 'work' defined", out)

        # Assert the config contains read context definition
        context_line = "context.work.read=project:Work\n"
        self.assertIn(context_line, self.t.taskrc_content)

        # Assert that it contains the definition only once
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

        # Assert the config does not contain write context definition
        context_line = "context.work.write=project:Work\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

        # Assert that legacy style was not used
        # Assert the config contains read context definition
        context_line = "context.work=project:Work\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

    def test_context_redefine_same_definition(self):
        """Test re-defining the context with the same definition."""
        self.t("context define work project:Work", input="y\ny\ny\n")
        code, out, err = self.t("context define work project:Work", input="y\ny\ny\n")
        self.assertIn("Context 'work' defined (read, write).", out)

        # Assert the config contains context definition
        context_line = "context.work.read=project:Work\n"
        self.assertIn(context_line, self.t.taskrc_content)
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

        context_line = "context.work.write=project:Work\n"
        self.assertIn(context_line, self.t.taskrc_content)
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

    def test_context_redefine_different_definition(self):
        """Test re-defining the context with different definition."""
        self.t("context define work project:Work", input="y\ny\ny\n")
        code, out, err = self.t("context define work +work", input="y\ny\ny\n")
        self.assertIn("Context 'work' defined", out)

        # Assert the config does not contain the old context definition
        self.assertNotIn("context.work.read=project:Work\n", self.t.taskrc_content)
        self.assertNotIn("context.work.write=project:Work\n", self.t.taskrc_content)

        # Assert the config contains context definition
        context_line = "context.work.read=+work\n"
        self.assertIn(context_line, self.t.taskrc_content)
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

        context_line = "context.work.write=+work\n"
        self.assertIn(context_line, self.t.taskrc_content)
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

    def test_context_define_invalid_for_write_due_to_modifier(self):
        """Test definition of a context that is not a valid write context."""
        self.t.config("confirmation", "off")
        code, out, err = self.t("context define urgent due.before:today")
        self.assertIn("Context 'urgent' defined", out)

        # Assert the config contains read context definition
        context_line = "context.urgent.read=due.before:today\n"
        self.assertIn(context_line, self.t.taskrc_content)

        # Assert that it contains the definition only once
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

        # Assert the config does not contain write context definition
        context_line = "context.urgent.write=due.before:today\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

        # Assert that the write context was not set at all
        self.assertNotIn("context.urgent.write=", self.t.taskrc_content)

        # Assert that legacy style was not used
        # Assert the config contains read context definition
        context_line = "context.urgent=due.before:today\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

    def test_context_define_invalid_for_write_due_to_operator(self):
        """Test definition of a context that is not a valid write context because it uses an OR operator."""
        self.t.config("confirmation", "off")
        code, out, err = self.t("context define urgent due:today or +next")
        self.assertIn("Context 'urgent' defined", out)

        # Assert the config contains read context definition
        context_line = "context.urgent.read=due:today or +next\n"
        self.assertIn(context_line, self.t.taskrc_content)

        # Assert that it contains the definition only once
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

        # Assert the config does not contain write context definition
        context_line = "context.urgent.write=due:today or +next\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

        # Assert that the write context was not set at all
        self.assertNotIn("context.urgent.write=", self.t.taskrc_content)

        # Assert that legacy style was not used
        # Assert the config contains read context definition
        context_line = "context.urgent=due:today or +next\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

    def test_context_define_invalid_for_write_due_to_tag_exclusion(self):
        """Test definition of a context that is not a valid write context because it contains a tag exclusion."""
        self.t.config("confirmation", "off")
        code, out, err = self.t("context define nowork due:today -work")
        self.assertIn("Context 'nowork' defined", out)

        # Assert the config contains read context definition
        context_line = "context.nowork.read=due:today -work\n"
        self.assertIn(context_line, self.t.taskrc_content)

        # Assert that it contains the definition only once
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

        # Assert the config does not contain write context definition
        context_line = "context.nowork.write=due:today -work\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

        # Assert that the write context was not set at all
        self.assertNotIn("context.nowork.write=", self.t.taskrc_content)

        # Assert that legacy style was not used
        # Assert the config contains read context definition
        context_line = "context.nowork=due:today -work\n"
        self.assertNotIn(context_line, self.t.taskrc_content)

    def test_context_delete(self):
        """Test simple context deletion."""
        self.t("context define work project:Work", input="y\ny\n")
        code, out, err = self.t("context delete work", input="y\ny\n")
        self.assertIn("Context 'work' deleted.", out)

        # Assert that taskrc does not countain context work definition
        self.assertFalse(any("context.work" in line for line in self.t.taskrc_content))

    def test_context_delete_undefined(self):
        """Test deletion of undefined context."""
        code, out, err = self.t.runError("context delete foo", input="y\n")
        self.assertIn("Context 'foo' not found.", err)

        # Assert that taskrc does not countain context work definition
        self.assertFalse(
            any("context.foo.read=" in line for line in self.t.taskrc_content)
        )
        self.assertFalse(
            any("context.foo.write=" in line for line in self.t.taskrc_content)
        )

    def test_context_delete_unset_after_removal(self):
        """Test that context is unset if its definition has been removed."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context work")
        code, out, err = self.t("context delete work", input="y\ny\n")
        self.assertIn("Context 'work' deleted.", out)

        # Assert that taskrc does not countain context work definition
        self.assertFalse(any("context.work=" in line for line in self.t.taskrc_content))
        self.assertFalse(
            any("context.work.read=" in line for line in self.t.taskrc_content)
        )
        self.assertFalse(
            any("context.work.write=" in line for line in self.t.taskrc_content)
        )

        # Aseert that the context is not set
        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)
        self.assertFalse(
            any(
                re.search(r"^context(\.(read|write))?=", line)
                for line in self.t.taskrc_content
            )
        )

    def test_context_list_active(self):
        """Test the 'context list' command."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")
        self.t("context home")
        code, out, err = self.t("context list")
        contains_work = (
            lambda line: "work" in line and "project:Work" in line and "no" in line
        )
        contains_home = (
            lambda line: "home" in line and "+home" in line and "yes" in line
        )

        # Assert that output contains work and home context definitions exactly
        # once
        self.assertEqual(len(list(filter(contains_work, out.splitlines()))), 1)
        self.assertEqual(len(list(filter(contains_home, out.splitlines()))), 1)

    def test_context_list_legacy(self):
        """Test the determination of legacy context definition."""
        self.t("config context.old project:Old", input="y\n")
        self.t("context old")
        code, out, err = self.t("context list")

        # Assert that "old" context has only the read component defined
        self.assertRegex(out, r"read\s+project:Old\s+yes")
        self.assertRegex(out, r"write\s+yes")

    def test_context_initially_empty(self):
        """Test that no context is set initially."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)
        self.assertFalse(
            any(re.search("^context=", line) for line in self.t.taskrc_content)
        )

    def test_context_setting(self):
        """Test simple context setting."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home home", input="y\ny\n")

        code, out, err = self.t("context home")
        self.assertIn("Context 'home' set.", out)
        self.assertIn("context=home\n", self.t.taskrc_content)

    def test_context_resetting(self):
        """Test resetting the same context."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        self.t("context home")
        code, out, err = self.t("context home")
        self.assertIn("Context 'home' set.", out)

        context_line = "context=home\n"
        self.assertEqual(self.t.taskrc_content.count(context_line), 1)

    def test_context_switching(self):
        """Test changing the context."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        # Switch to home context
        code, out, err = self.t("context home")
        self.assertIn("Context 'home' set.", out)
        self.assertEqual(self.t.taskrc_content.count("context=home\n"), 1)

        # Switch to work context
        code, out, err = self.t("context work")
        self.assertIn("Context 'work' set.", out)
        self.assertNotIn("context=home\n", self.t.taskrc_content)
        self.assertEqual(self.t.taskrc_content.count("context=work\n"), 1)

        # Switch back to home context
        code, out, err = self.t("context home")
        self.assertIn("Context 'home' set.", out)
        self.assertNotIn("context=work\n", self.t.taskrc_content)
        self.assertEqual(self.t.taskrc_content.count("context=home\n"), 1)

    def test_context_unsetting(self):
        """Test removing the context."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        self.t("context home")
        code, out, err = self.t("context none")

        # Assert expected output.
        self.assertIn("Context unset.", out)

        # Assert no context definition in the taskrc
        contains_any_context = lambda line: re.match("^context=", line)
        self.assertFalse(
            any(contains_any_context(line) for line in self.t.taskrc_content)
        )

        # Assert no context showing up using show subcommand
        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)

    def test_context_unsetting_after_switching(self):
        """Test unsetting the context after changing the context around."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        # Switch to contexts around
        self.t("context home")
        self.t("context work")
        self.t("context home")

        # Unset the context
        code, out, err = self.t("context none")

        # Assert expected output.
        self.assertIn("Context unset.", out)

        # Assert no context definition in the taskrc
        contains_any_context = lambda line: re.match("^context=", line)
        self.assertFalse(
            any(contains_any_context(line) for line in self.t.taskrc_content)
        )

        # Assert no context showing up using show subcommand
        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)

    def test_context_unsetting_with_no_context_set(self):
        """Test removing the context when no context is set."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        code, out, err = self.t.runError("context none")

        # Assert expected output.
        self.assertIn("Context not unset.", err)

        # Assert no context definition in the taskrc
        contains_any_context = lambda line: re.match("^context=", line)
        self.assertFalse(
            any(contains_any_context(line) for line in self.t.taskrc_content)
        )

        # Assert no context showing up using show subcommand
        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)

    def test_context(self):
        """Test the _context command."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")
        code, out, err = self.t("_context")

        # Assert expected output.
        self.assertIn("work", out.splitlines())
        self.assertIn("home", out.splitlines())
        self.assertEqual(len(out.splitlines()), 2)

    def test_context_completion(self):
        """Test the _context command with some context set."""
        self.t("context define work project:Work", input="y\ny\n")
        self.t("context define home +home", input="y\ny\n")

        # Activate some context
        self.t("context work")
        code, out, err = self.t("_context")

        # Assert expected output.
        self.assertIn("work", out.splitlines())
        self.assertIn("home", out.splitlines())
        self.assertEqual(len(out.splitlines()), 2)


class ContextEvaluationTest(TestCase):
    def setUp(self):
        self.t = Task()

        self.t.config("confirmation", "off")

        # Setup contexts
        self.t("context define work project:Work")
        self.t("context define home +home")
        self.t("context define today due:today")

        # Setup tasks
        self.t('add project:Work "work task"')
        self.t('add +home "home task"')
        self.t('add project:Work due:today "work today task"')
        self.t('add +home due:today "home today task"')

    def test_context_evaluation(self):
        """Test the context applied with report list command."""
        code, out, err = self.t("list")

        # Assert all the tasks are present in the output
        self.assertIn("work task", out)
        self.assertIn("home task", out)
        self.assertIn("work today task", out)
        self.assertIn("home today task", out)

        # Set the home context and rerun the report
        self.t("context home")
        code, out, err = self.t("list")

        # Assert all the tasks with the home tag are present in the output
        self.assertNotIn("work task", out)
        self.assertIn("home task", out)
        self.assertNotIn("work today task", out)
        self.assertIn("home today task", out)

    def test_context_evaluation_switching(self):
        """Test swtiching context using the list report."""
        code, out, err = self.t("list")

        # Assert all the tasks are present in the output
        self.assertIn("work task", out)
        self.assertIn("home task", out)
        self.assertIn("work today task", out)
        self.assertIn("home today task", out)

        # Set the home context and rerun the report
        self.t("context home")
        code, out, err = self.t("list")

        # Assert all the tasks with the home tag are present in the output
        self.assertNotIn("work task", out)
        self.assertIn("home task", out)
        self.assertNotIn("work today task", out)
        self.assertIn("home today task", out)

        # Set the work context and rerun the report
        self.t("context work")
        code, out, err = self.t("list")

        # Assert all the tasks with the home tag are present in the output
        self.assertIn("work task", out)
        self.assertNotIn("home task", out)
        self.assertIn("work today task", out)
        self.assertNotIn("home today task", out)

        # Set the today context and rerun the report
        self.t("context today")
        code, out, err = self.t("list")

        # Assert all the tasks with the home tag are present in the output
        self.assertNotIn("work task", out)
        self.assertNotIn("home task", out)
        self.assertIn("work today task", out)
        self.assertIn("home today task", out)

    def test_context_evaluation_unset(self):
        """Test unsetting context with report list command."""
        self.t("context home")
        code, out, err = self.t("list")

        # Assert all the tasks home tagged tasks are present
        self.assertNotIn("work task", out)
        self.assertIn("home task", out)
        self.assertNotIn("work today task", out)
        self.assertIn("home today task", out)

        # Set the context to none
        self.t("context none")
        code, out, err = self.t("list")

        # Assert all the tasks are present in the output
        self.assertIn("work task", out)
        self.assertIn("home task", out)
        self.assertIn("work today task", out)
        self.assertIn("home today task", out)

    def test_context_evaluation_with_user_filters(self):
        """Test the context applied with report list command combined with user filters."""

        # Set the home context
        self.t("context home")
        code, out, err = self.t("list due:today")

        # Assert all the tasks are present in the output
        self.assertNotIn("work task", out)
        self.assertNotIn("home task", out)
        self.assertNotIn("work today task", out)
        self.assertIn("home today task", out)

        # Set the work context and rerun the report
        self.t("context work")
        code, out, err = self.t("list due:today")

        # Assert all the tasks are present in the output
        self.assertNotIn("work task", out)
        self.assertNotIn("home task", out)
        self.assertIn("work today task", out)
        self.assertNotIn("home today task", out)

    def test_context_not_applied_on_id_filters(self):
        """
        Test that context is not applied when explicit ID
        filters are used.
        """

        self.t("context home")

        # Try task not included in context
        output = self.t("1 list")[1]

        # Assert that ID filter works even if it does not match the context
        self.assertIn("work task", output)
        self.assertNotIn("home task", output)
        self.assertNotIn("work today task", output)
        self.assertNotIn("home today task", output)

        # Try task included in context
        output = self.t("2 list")[1]

        # Assert that ID filter works if it does match
        # the context (sanity check)
        self.assertNotIn("work task", output)
        self.assertIn("home task", output)
        self.assertNotIn("work today task", output)
        self.assertNotIn("home today task", output)

        # Test for combination of IDs
        output = self.t("1 2 list")[1]

        # Assert that ID filter works if it partly matches
        # and partly does not match the context
        self.assertIn("work task", output)
        self.assertIn("home task", output)
        self.assertNotIn("work today task", output)
        self.assertNotIn("home today task", output)

    def test_context_not_applied_on_uuid_filters(self):
        """
        Test that context is not applied when explicit UUID
        filters are used.
        """

        self.t("context home")
        first_uuid = self.t("_get 1.uuid")[1]
        second_uuid = self.t("_get 2.uuid")[1]

        # Try task not included in context
        output = self.t("%s list" % first_uuid)[1]

        # Assert that UUID filter works even if it does not match
        # the context
        self.assertIn("work task", output)
        self.assertNotIn("home task", output)
        self.assertNotIn("work today task", output)
        self.assertNotIn("home today task", output)

        # Try task included in context
        output = self.t("%s list" % second_uuid)[1]

        # Assert that UUID filter works if it does match
        # the context (sanity check)
        self.assertNotIn("work task", output)
        self.assertIn("home task", output)
        self.assertNotIn("work today task", output)
        self.assertNotIn("home today task", output)

        # Test for combination of UUIDs
        output = self.t("%s %s list" % (first_uuid, second_uuid))[1]

        # Assert that UUID filter works if it partly matches
        # and partly does not match the context
        self.assertIn("work task", output)
        self.assertIn("home task", output)
        self.assertNotIn("work today task", output)
        self.assertNotIn("home today task", output)

    def test_context_ignored(self):
        """Test the context is not applied with report list command if
        report.list.context is set to 0."""

        # Turn off context for this report
        self.t.config("report.list.context", "0")

        # Get the tasks
        code, out, err = self.t("list")

        # Assert all the tasks are present in the output
        self.assertIn("work task", out)
        self.assertIn("home task", out)
        self.assertIn("work today task", out)
        self.assertIn("home today task", out)

        # Set the home context and rerun the report
        self.t("context home")

        code, out, err = self.t("list")

        # Assert nothing changed - all the tasks are present in the output
        self.assertIn("work task", out)
        self.assertIn("home task", out)
        self.assertIn("work today task", out)
        self.assertIn("home today task", out)


class ContextErrorHandling(TestCase):
    def setUp(self):
        self.t = Task()

    def test_list_empty(self):
        """Verify 'task context list' with no contexts yields error"""
        code, out, err = self.t.runError("context list")
        self.assertIn("No contexts defined.", err)

    def test_define_empty(self):
        """Verify 'task context define' with no contexts yields error"""
        code, out, err = self.t.runError("context define")
        self.assertIn("Both context name and its definition must be provided.", err)

    def test_delete_empty(self):
        """Verify 'task context delete' with no contexts yields error"""
        code, out, err = self.t.runError("context delete")
        self.assertIn("Context name needs to be specified.", err)

    def test_set_missing(self):
        """Verify 'task context missing' with no contexts yields error"""
        code, out, err = self.t.runError("context missing")
        self.assertIn("Context 'missing' not found.", err)

    def test_set_multi(self):
        """Verify 'task context one\\ two' with no contexts yields error"""
        code, out, err = self.t.runError("context one\\ two")
        self.assertIn("Context 'one two' not found.", err)

    def test_show_missing(self):
        """Verify 'task context show' with no contexts yields correct information"""
        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)

    def test_show_present(self):
        """Verify 'task context show' with contexts works"""
        self.t.config("confirmation", "off")
        code, out, err = self.t("context define work +work")
        self.assertIn(
            "Context 'work' defined (read, write). Use 'task context work' to activate.",
            out,
        )

        code, out, err = self.t("context work")
        self.assertIn("Context 'work' set. Use 'task context none' to remove.", out)

        code, out, err = self.t("context show")
        self.assertIn("Context 'work' with", out)
        self.assertIn("read filter: '+work'", out)
        self.assertIn("write filter: '+work'", out)
        self.assertIn("is currently applied", out)

        code, out, err = self.t("context none")
        self.assertIn("Context unset.", out)

        code, out, err = self.t("context show")
        self.assertIn("No context is currently applied.", out)


class TestBug1734(TestCase):
    def setUp(self):
        self.t = Task()
        self.t("add zero")
        self.t("add one +tag")
        self.t("context define foo +tag", input="y\nn\n")

    def test_calendar(self):
        """The 'calendar' command should not fail when a context is active"""
        code, out, err = self.t("calendar")


# TODO Prove context does not interfere with export
# TODO Prove context does not interfere with undo
# TODO Prove context does not interfere with helper commands


if __name__ == "__main__":
    from simpletap import TAPTestRunner

    unittest.main(testRunner=TAPTestRunner())

# vim: ai sts=4 et sw=4 ft=python syntax=python
