#include "llvm/Pass.h"
#include "llvm/Function.h"
#include "llvm/Type.h"
#include "llvm/InstrTypes.h"
#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/raw_ostream.h"

#include <stdio.h>

using namespace llvm;

const int REP_COUNT = 3;

namespace {
  struct TestPass : public FunctionPass {
    static char ID;
    TestPass() : FunctionPass(ID) {}

    virtual bool runOnFunction(Function &F) {
      LLVMContext &Ctx = F.getContext();

      errs() << "run on func\n";
      
      // first identify allocations
      std::vector<AllocaInst*> bitAllocs;
      for (auto& B : F) {
        for (auto& I : B) {
          auto* op = &I;
          errs() << ";" << op->getOpcodeName() << "--" << op->getType()->isPointerTy() << "\n";

          std::string op_code = op->getOpcodeName();
          if (op_code == "alloca") { // Only one operand
            AllocaInst* alloca_op = (AllocaInst*) op;
            bitAllocs.push_back(alloca_op);
          }
        }
      }

      // then insert a new allocation/copy of the allocation


      // then traverse the uses of the original qbit and copy to the new allocs


      bool modified = false;
      for (AllocaInst* alloca_op : bitAllocs) {
        IRBuilder<> builder(alloca_op);
        builder.SetInsertPoint(alloca_op->getParent(), ++builder.GetInsertPoint());
        std::vector<Value*> newOps;
        Value* newOp;
        Type* alloca_type = alloca_op->getAllocatedType();
        Value* alloca_size = alloca_op->getArraySize();
        for (int i = 0; i < REP_COUNT - 1; i++) {
          Value* newAlloca = builder.CreateAlloca(alloca_type, alloca_size);
          Value* newCpy = builder.CreateMemCpy(newAlloca, alloca_op, alloca_size, 2);
          newOps.push_back(newAlloca);
        }
        
        auto next_op = (Instruction*)alloca_op;
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
                if (cur_user->getOperand(j) == alloca_op)
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
      
      return modified;
    }
  };
}

char TestPass::ID = 0;

// Register the pass so `opt -test` runs it.
static RegisterPass<TestPass> X("test", "a useless pass");
