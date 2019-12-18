#include "llvm/Pass.h"
#include "llvm/Function.h"
#include "llvm/Type.h"
#include "llvm/InstrTypes.h"
#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/raw_ostream.h"

#include <stdio.h>

// to load file with branch info give command line arg with name (might need multiple for different loops, so json file?)
// https://stackoverflow.com/questions/13626993/is-it-possible-to-add-arguments-for-user-defined-passes-in-llvm

using namespace llvm;

const int REP_COUNT = 3;

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
      int skip = 0;
      for (auto& B : F) {
        for (auto& I : B) {
          if (skip > 0) {
            skip--;
            continue;
          }
          auto* op = &I;
          IRBuilder<> builder(op);
          builder.SetInsertPoint(&B, ++builder.GetInsertPoint());
          std::vector<Value*> newOps;
          Value* newOp;
          errs() << ";" << op->getOpcodeName() << "--" << op->getType()->isPointerTy() << "\n";

          std::string op_code = op->getOpcodeName();
          if (op_code == "alloca") { // Only one operand
            AllocaInst* alloca_op = (AllocaInst*) op;
            Type* alloca_type = alloca_op->getAllocatedType();
            Value* alloca_size = alloca_op->getArraySize();
            for (int i = 0; i < REP_COUNT - 1; i++) {
              Value* newAlloca = builder.CreateAlloca(alloca_type, alloca_size);
              Value* newCpy = builder.CreateMemCpy(newAlloca, alloca_op, alloca_size, 2);
              newOps.push_back(newAlloca);
            }
            skip = REP_COUNT * 3;
          }
          
          // errs() << op->getNumUses() << "--\n";
          if (newOps.size() == 0)
            continue;
          
          auto next_op = op;
          // I can't figure out the recursion here tonight...just too tired.
          for (int i = 0; i < 1; i++) {
          // while (next_op->getNumUses() > 0) {
            std::vector<Value*> nextOps;
            for (auto iter = next_op->use_begin(); !iter.atEnd(); iter++) {
              User* cur_user = *iter;
              next_op = (Instruction*) cur_user;
              for (int i = 0; i < REP_COUNT - 1; i++) {
                auto new_instr = next_op->clone();
                new_instr = builder.Insert(new_instr);
                nextOps.push_back(new_instr);
                for (int j = 0; j < cur_user->getNumOperands(); j++)
                  if (cur_user->getOperand(j) == op)
                    new_instr->setOperand(j, newOps[i]);
              }
            }
            newOps = nextOps;
          }
          // for (auto& U : op->uses()) {
          //   User* user = U.getUser();  // A User is anything with operands.
          //   user->setOperand(U.getOperandNo(), newOp);
          // }
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
