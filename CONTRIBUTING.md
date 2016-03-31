How to contribute code
======================

1. Create an issue on Gitlab.
2. If you are adding new functionality, create a stub implementation
   of the desired argument/function/class/etc.
3. Write a test for your new functionality/bugfix and run it, ensuring
   that it fails on the current implementation:
   ```
   py.test tests/test_my_code.py
   ```
   NameErrors, ImportErrors, SyntaxErrors, etc. do *not* count.
4. Implement your new functionality/bugfix.
5. Run the test again, ensuring that it now passes.
6. Run all tests and style checks, ensuring that they pass:
   ```
   py.test tests
   bash check-style.bash
   ```
7. Push your changes to a feature branch on Gitlab (e.g., called
   `n-issue-abbrev` where `n` is the issue number and `issue-abbrev`
   is a very short abbreviation of the issue title) and ensure that the
   build passes.  The build is defined in `.gitlab-ci.yml`; if it
   fails, you may wish to consult that file.
8. If you've made multiple commits, please squash them and
   `git push -f` to the feature branch.
9. Create a merge request for your feature branch into `master`,
   referencing the Gitlab issue.
