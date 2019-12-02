#include "llvm/Pass.h"
#include "llvm/Function.h"
#include "llvm/Support/raw_ostream.h"

#include <stdio.h>

// to load file with branch info give command line arg with name (might need multiple for different loops, so json file?)
// https://stackoverflow.com/questions/13626993/is-it-possible-to-add-arguments-for-user-defined-passes-in-llvm

using namespace llvm;

namespace {
  // TODO potentially want a LoopPass b/c want to trace across within a loop nest and not outside
  struct TestPass : public FunctionPass {
    static char ID;
    TestPass() : FunctionPass(ID) {}

    virtual bool runOnFunction(Function &F) {

      errs() << "run on func\n";
      // ret whether code was modified or not
      return false;
    }
  };
}

char TestPass::ID = 0;

// Register the pass so `opt -test` runs it.
static RegisterPass<TestPass> X("test", "a useless pass");
