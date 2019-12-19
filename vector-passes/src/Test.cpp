#include "llvm/Pass.h"
#include "llvm/Function.h"
#include "llvm/Type.h"
#include "llvm/InstrTypes.h"
#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"

#include <stdio.h>

using namespace llvm;

// command line argument specified as --qvlen 
static cl::opt<int> REP_COUNT("qvlen", cl::desc("Specify the vector length for quantum pass"), cl::value_desc("vlen"), cl::init(3));

namespace {
  struct TestPass : public FunctionPass {
    static char ID;
    TestPass() : FunctionPass(ID) {}

    virtual bool runOnFunction(Function &F) {
      LLVMContext &Ctx = F.getContext();
      errs() << "vlen " << REP_COUNT << '\n';
      errs() << "run on func " << F.getName() << "\n";
      
      // first identify allocations
      std::vector<AllocaInst*> bitAllocs;
      for (auto& B : F) {
        for (auto& I : B) {
          auto* op = &I;
          std::string op_code = op->getOpcodeName();
          if (op_code == "alloca") {
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
          Twine new_name = alloca_op->getName() + "_" + Twine(i);
          Value* newAlloca = builder.CreateAlloca(alloca_type, alloca_size, new_name);
          // Value* newCpy = builder.CreateMemCpy(newAlloca, alloca_op, alloca_size, 2);
          newOps.push_back(newAlloca);
        }
        
        std::vector<Instruction*> op_list;
        // Inefficient queue setup, but whatever
        op_list.insert(op_list.begin(), (Instruction*)alloca_op);
        // I can't figure out the recursion here tonight...just too tired.
        for (int tmp = 0; tmp < 2; tmp++) {
        // while (next_op->getNumUses() > 0) {
          std::vector<Value*> nextOps;
          Instruction* cur_op = op_list[op_list.size() - 1];
          op_list.pop_back();
          for (auto iter = cur_op->use_begin(); !iter.atEnd(); iter++) {
            User* cur_user = *iter;
            auto next_op = (Instruction*) cur_user;
            op_list.insert(op_list.begin(), next_op);
            for (int i = 0; i < REP_COUNT - 1; i++) {
              auto new_instr = next_op->clone();
              builder.SetInsertPoint(next_op->getParent(), ++builder.GetInsertPoint());
              new_instr = builder.Insert(new_instr);
              nextOps.push_back(new_instr);
              for (int j = 0; j < cur_user->getNumOperands(); j++)
                if (cur_user->getOperand(j) == cur_op)
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
