////////////////////////////////////////////////////////////////////////////////
//
// Copyright 2006 - 2021, Tomas Babej, Paul Beckingham, Federico Hernandez.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// https://www.opensource.org/licenses/mit-license.php
//
////////////////////////////////////////////////////////////////////////////////

#ifndef INCLUDED_CMDIDS
#define INCLUDED_CMDIDS

#include <Command.h>

#include <string>

class CmdIDs : public Command {
 public:
  CmdIDs();
  int execute(std::string&);

 private:
  std::string compressIds(const std::vector<int>&);
};

class CmdCompletionIds : public Command {
 public:
  CmdCompletionIds();
  int execute(std::string&);
};

class CmdZshCompletionIds : public Command {
 public:
  CmdZshCompletionIds();
  int execute(std::string&);
};

class CmdUUIDs : public Command {
 public:
  CmdUUIDs();
  int execute(std::string&);
};

class CmdCompletionUuids : public Command {
 public:
  CmdCompletionUuids();
  int execute(std::string&);
};

class CmdZshCompletionUuids : public Command {
 public:
  CmdZshCompletionUuids();
  int execute(std::string&);
};

#endif
////////////////////////////////////////////////////////////////////////////////
