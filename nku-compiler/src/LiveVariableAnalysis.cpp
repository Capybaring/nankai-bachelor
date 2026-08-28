#include "LiveVariableAnalysis.h"
#include "MachineCode.h"
#include <algorithm>
#include <iostream>
void LiveVariableAnalysis::pass(MachineUnit *unit)
{
    std::cout << "开始对整个单元进行活跃变量分析。" << std::endl;
    for (auto &func : unit->getFuncs())
    {
        std::cout << "处理函数：" << func << std::endl;
        computeUsePos(func);
        std::cout << "计算使用位置完成。" << std::endl;
        computeDefUse(func);
        std::cout << "计算定义和使用完成。" << std::endl;
        iterate(func);
        std::cout << "迭代计算活跃变量完成。" << std::endl;
    }
    std::cout << "整个单元的活跃变量分析完成。" << std::endl;
}

void LiveVariableAnalysis::pass(MachineFunction *func)
{
    std::cout << "开始对函数进行活跃变量分析：" << func << std::endl;
    computeUsePos(func);
    std::cout << "计算使用位置完成。" << std::endl;
    computeDefUse(func);
    std::cout << "计算定义和使用完成。" << std::endl;
    iterate(func);
    std::cout << "迭代计算活跃变量完成。" << std::endl;
    std::cout << "函数的活跃变量分析完成：" << func << std::endl;
}

void LiveVariableAnalysis::computeDefUse(MachineFunction *func)
{
    std::cout << "开始计算定义和使用。" << std::endl;
    for (auto &block : func->getBlocks())
    {
        std::cout << "处理基本块：" << block << std::endl;
        for (auto inst = block->getInsts().begin(); inst != block->getInsts().end(); inst++)
        {
            if(!*inst)
                continue;
            auto user = (*inst)->getUse();
            std::set<MachineOperand *> temp(user.begin(), user.end());
            set_difference(temp.begin(), temp.end(),
                           def[block].begin(), def[block].end(), inserter(use[block], use[block].end()));
            auto defs = (*inst)->getDef();
            for (auto &d : defs)
                def[block].insert(all_uses[*d].begin(), all_uses[*d].end());
        }
    }
    std::cout << "定义和使用计算完成。" << std::endl;
}

void LiveVariableAnalysis::iterate(MachineFunction *func)
{
    std::cout << "开始迭代计算活跃变量。" << std::endl;
    for (auto &block : func->getBlocks())
        block->getLiveIn().clear();
    bool change;
    change = true;
    while (change)
    {
        change = false;
        for (auto &block : func->getBlocks())
        {
            block->getLiveOut().clear();
            auto old = block->getLiveIn();
            for (auto &succ : block->getSuccs())
                block->getLiveOut().insert(succ->getLiveIn().begin(), succ->getLiveIn().end());
            block->getLiveIn() = use[block];
            std::vector<MachineOperand *> temp;
            set_difference(block->getLiveOut().begin(), block->getLiveOut().end(),
                           def[block].begin(), def[block].end(), inserter(block->getLiveIn(), block->getLiveIn().end()));
            if (old != block->getLiveIn())
                change = true;
        }
    }
    std::cout << "迭代计算活跃变量完成。" << std::endl;
}

void LiveVariableAnalysis::computeUsePos(MachineFunction *func)
{
    std::cout << "开始计算使用位置。" << std::endl;
    for (auto &block : func->getBlocks())
    {
        if (block->getInsts().empty())
        {
            std::cout << "跳过空基本块：" << block << std::endl;
            continue;
        }
        std::cout << "处理基本块：" << block << std::endl;
        for (auto &inst : block->getInsts())
        {
            if(!inst)
                continue;
            std::cout << "处理指令：" << inst << std::endl;
            auto uses = inst->getUse();
            for (auto &use : uses)
            {
            std::cout << "使用操作数：" << use << std::endl;
            all_uses[*use].insert(use);
            }
        }
    }
    std::cout << "使用位置计算完成。" << std::endl;
}