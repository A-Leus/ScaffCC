#include "llvm/Pass.h"
#include "llvm/Function.h"
#include "llvm/Type.h"
#include "llvm/InstrTypes.h"
#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"


#include <unordered_map>
#include <queue>
#include <stdio.h>

using namespace llvm;

// command line argument specified as --qvlen 
static cl::opt<int> REP_COUNT("qvlen", cl::desc("Specify the vector length for quantum pass"), cl::value_desc("vlen"), cl::init(3));

namespace {
  // store metadata for each original instruction during the pass
  typedef struct InstMetadata_t {
    std::vector<llvm::Instruction*> clones;
    InstMetadata_t(std::vector<llvm::Instruction*> clones) {
      this->clones = clones;
    }
    InstMetadata_t() {

    }
  } InstMetadata_t;

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
          if (op_code == "alloca") { // Only one operand
            AllocaInst* alloca_op = (AllocaInst*) op;
            bitAllocs.push_back(alloca_op);
          }
        }
      }

      // initially seed the work queue with the allocs
      std::queue<llvm::Instruction*> workQueue;
      // Hash table storing extra meta data for the processed instructions
      std::unordered_map<llvm::Instruction*, InstMetadata_t> metaTable;


      // then insert a new allocation/copy of the allocation
      // data structure is [orig_alloc][copy#]
      //std::unordered_map<Instruction*, std::vector<AllocaInst*>> newAllocs;
      for (AllocaInst* alloca_op : bitAllocs) {

        // std::vector<Instruction*> newInsts;

        // IRBuilder<> builder(alloca_op);
        // builder.SetInsertPoint(alloca_op->getParent(), ++builder.GetInsertPoint());
        // Type* alloca_type = alloca_op->getAllocatedType();
        // Value* alloca_size = alloca_op->getArraySize();
        // for (int i = 1; i < REP_COUNT; i++) {
        //   // need a name otherwise later quantum passes fail
        //   Twine new_name = alloca_op->getName() + "_" + Twine(i);
        //   AllocaInst* new_alloca = builder.CreateAlloca(alloca_type, alloca_size, new_name);
          
        //   newInsts.push_back(new_alloca);
        // }

        // add to work queue and set metadata
        workQueue.push((llvm::Instruction*)alloca_op);
        //metaTable[alloca_op] = InstMetadata_t(newInsts);
      }

      // then traverse the uses of the original and copy if the original has already been copied
      // this needs to be a bfs algorithm where can't process (copy and populate) instruction
      // until deps have been copied and populated

      // keep going untile work queue is empty
      while (!workQueue.empty()) {
        // get instruction to process
        auto &I = workQueue.front();
        workQueue.pop();
        
        errs() << *I << "\n";

        // do action on the instruction (copy and propagate copied deps)
        IRBuilder<> builder(I);
        builder.SetInsertPoint(I->getParent(), ++builder.GetInsertPoint());
        std::vector<llvm::Instruction*> newInsts;
        for (int i = 1; i < REP_COUNT; i++) {
          auto new_instr = I->clone();
          new_instr = builder.Insert(new_instr);
          
          errs() << *new_instr << "\n";

          if (new_instr->getOpcodeName() == "alloca") {
            Twine new_name = I->getName() + "_" + Twine(i);
            errs() << "set name " << new_name << "\n";
            new_instr->setName(new_name);
          }

          // for each operand get the copy stored in the metadata for the orignal instruction
          for (int j = 0; j < new_instr->getNumOperands(); j++) {
            // get metadata for this dependency of the original instruction
            llvm::Instruction* def_inst = nullptr;
            auto orig_operand = dyn_cast<llvm::Instruction>(I->getOperand(j));
            if (orig_operand != nullptr) { // instruction dep
              errs() << "operand\n";
              if (metaTable.count(orig_operand)) {
                def_inst = metaTable[orig_operand].clones[i - 1];
              }
              
              new_instr->setOperand(j, def_inst);
            }
            else { // normal value
              errs() << "normal val\n";
              new_instr->setOperand(j, I->getOperand(j));
            }
          }

          newInsts.push_back(new_instr);
        }

        metaTable[I] = InstMetadata_t(newInsts);


        // check uses of this original instruction and try to put future instructions on the work queue if rdy
        for (auto iter = I->use_begin(); !iter.atEnd(); iter++) {
          llvm::User* cur_user = *iter;
          llvm::Instruction* nextI = (llvm::Instruction*) cur_user;

          // get all dependencies, if all in the metaTable, then deps met and can be added to the queue
          bool depsMet = true;
          for (int i = 0; i < nextI->getNumOperands(); i++) {
            auto inst_dep = dyn_cast<llvm::Instruction>(nextI->getOperand(i));
            if (inst_dep)
              if (!metaTable.count(inst_dep)) depsMet = false;
          }

          if (depsMet) {
            workQueue.push(nextI);
          }
        }
      }

      return (REP_COUNT > 1);
    }
  };
}

char TestPass::ID = 0;

// Register the pass so `opt -test` runs it.
static RegisterPass<TestPass> X("test", "a useless pass");
