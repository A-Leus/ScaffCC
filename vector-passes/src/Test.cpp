#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/IR/IRBuilder.h"
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
      LLVMContext &Ctx = F.getContext();

      errs() << "run on func\n";
      // ret whether code was modified or not
      
      bool modified = false;
      for (auto& B : F) {
        for (auto& I : B) {
          auto* op = &I;
          IRBuilder<> builder(op);
          builder.SetInsertPoint(&B, ++builder.GetInsertPoint());
          Value* newOp = NULL;
          std::vector<Value*> opers;
          // newOp = op->clone();
          // op->setOperand(0);
          for (int i = 0; i < op->getNumOperands(); i++) {
            errs() << op->getOperand(i)->getName();
          }
          errs() << ";" << op->getOpcodeName() << "--" << op->getType()->isPointerTy() << "\n";
          // errs() << op->getNumUses() << "--\n";
          if (!newOp)
            continue;
          for (auto& U : op->uses()) {
            User* user = U.getUser();  // A User is anything with operands.
            user->setOperand(U.getOperandNo(), newOp);
          }
          modified = true;
        }
      }
      return modified;
    }
  };
}

char TestPass::ID = 0;

// Register the pass so `opt -test` runs it.
static RegisterPass<TestPass> X("test", "a useless pass");
