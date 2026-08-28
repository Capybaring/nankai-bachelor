%code top{
    #include <iostream>
    #include <assert.h>
    #include "parser.h"
    extern Ast ast;
    int yylex();
    int yyerror( char const * );
}

%code requires {
    #include "Ast.h"
    #include "SymbolTable.h"
    #include "Type.h"
}

%union {
    int itype;
    char* strtype;
    StmtNode* stmttype;
    ExprNode* exprtype;
    Type* type;

}

%start Program
%token <strtype> ID 
%token <itype> INTEGER
%token IF ELSE
%token CONST
%token INT VOID
%token LP RP LB RB SEMICOLON COLON COMMA LBRACKET RBRACKET
%token ADD SUB MUL DIV MOD SELFADD SELFDEC 
%token SCAN PRINT
%token LESS GREATER EQ NEQ GEQ LEQ
%token ASSIGN
%token OR AND NOT
%token FOR WHILE BREAK CONTINUE MAIN RETURN

%nterm <stmttype> Stmts Stmt  
%nterm <stmttype> AssignStmt BlockStmt  IfStmt  DeclStmt FuncDefStmt
%nterm <stmttype> WhileStmt ForStmt ContinueStmt BreakStmt IOStmt ReturnStmt 
%nterm <stmttype> ForInitialStmt 
%nterm <stmttype> ConstDefList ConstDef ConstInitVal VarDefList VarDef VarInitVal ArrConstIndices ArrValIndices ConstInitValList VarInitValList
%nterm <exprtype> Exp UnaryExp PrimaryExp LVal AddExp MulExp Cond LOrExp LAndExp  RelExp    
%nterm <exprtype> ConstExp
%nterm <type> Type

%precedence THEN
%precedence ELSE
%%
Program
    : 
    Stmts {
        ast.setRoot($1);
    }
    ;
Stmts
    : Stmt {
        SeqNode* node = new SeqNode();
        node->addNext(dynamic_cast<StmtNode*>($1));
        $$ = dynamic_cast<StmtNode*>(node);
    }
    | Stmts Stmt{
        SeqNode* node = dynamic_cast<SeqNode*>($1);
        node->addNext(dynamic_cast<StmtNode*>($2));
        $$ = dynamic_cast<StmtNode*>(node);
    }
    ;
Stmt
    : AssignStmt {$$=$1;}
    | BlockStmt {$$=$1;}
    | WhileStmt {$$=$1;}
    | ForStmt {$$=$1;}
    | IfStmt {$$=$1;}
    | ContinueStmt {$$=$1;}
    | BreakStmt {$$=$1;}
    | DeclStmt {$$=$1;}
    | FuncDefStmt {$$=$1;} 
    | IOStmt {$$=$1;}
    | ReturnStmt {$$=$1;}
    ;
AssignStmt
    :LVal ASSIGN Exp {
        $$ = new AssignStmt($1, $3);
    }
    | LVal ASSIGN Exp SEMICOLON {
        $$ = new AssignStmt($1, $3);
    }
    | LVal SELFADD {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($1, new BinaryExpr(se, BinaryExpr::ADD, $1, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | LVal SELFADD SEMICOLON {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($1, new BinaryExpr(se, BinaryExpr::ADD, $1, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | LVal SELFDEC {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($1, new BinaryExpr(se, BinaryExpr::SUB, $1, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | LVal SELFDEC SEMICOLON {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($1, new BinaryExpr(se, BinaryExpr::SUB, $1, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | SELFDEC LVal {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($2, new BinaryExpr(se, BinaryExpr::SUB, $2, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | SELFDEC LVal SEMICOLON {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($2, new BinaryExpr(se, BinaryExpr::SUB, $2, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | SELFADD LVal {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($2, new BinaryExpr(se, BinaryExpr::ADD, $2, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    | SELFADD LVal SEMICOLON {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new AssignStmt($2, new BinaryExpr(se, BinaryExpr::ADD, $2, new Constant(new ConstantSymbolEntry(TypeSystem::intType, 1))));
    }
    ;

BlockStmt
    : LB {identifiers = new SymbolTable(identifiers);} Stmts RB {
        $$ = new CompoundStmt($3);
        SymbolTable *top = identifiers;
        identifiers = identifiers->getPrev();
        delete top;
    }
    | LB RB {
        $$ = new CompoundStmt(nullptr);
    }
    ;

WhileStmt
    : WHILE LP Cond RP Stmt {
        $$=new WhileStmt($3,$5);
    }
    ;

ForStmt
    : FOR LP ForInitialStmt SEMICOLON Cond SEMICOLON AssignStmt RP Stmt {
        $$=new ForStmt($3,$5,$7,$9);
        identifiers = identifiers->getPrev();
    }
    ;

ForInitialStmt
    : Type ID ASSIGN Exp{
        identifiers = new SymbolTable(identifiers);
        Type* type = TypeSystem::intType;
        SymbolEntry *se = new IdentifierSymbolEntry(type, $2, identifiers->getLevel());
        identifiers->install($2, se);
        $$ = new DefNode(new Id(se), dynamic_cast<Node*>($4));
    }

FuncDefStmt
    : Type MAIN LP RP BlockStmt {
        Type *funcType = new FunctionType($1,{});
        SymbolEntry *se = new IdentifierSymbolEntry(funcType, "main", identifiers->getLevel());
        identifiers->install("main", se); 
        identifiers = new SymbolTable(identifiers); 
        $$ = new FunctionDef(se, $5);
    }
    ;

IfStmt
    : IF LP Cond RP Stmt %prec THEN {
        $$ = new IfStmt($3, $5);
    }
    | IF LP Cond RP Stmt ELSE Stmt {
        $$ = new IfElseStmt($3, $5, $7);
    }
    ;

BreakStmt
    : BREAK SEMICOLON { 
        if(whileStack.empty()){
            $$ = new BreakStmt(nullptr);
        }
        else{
            $$ = new BreakStmt(whileStack.top());
        }
    }
    ;
ContinueStmt
    : CONTINUE SEMICOLON { 
        if(whileStack.empty()){
            $$ = new ContinueStmt(nullptr);
        }
        else{
            $$ = new ContinueStmt(whileStack.top());
        }
    }
    ;

DeclStmt
    :   CONST Type ConstDefList SEMICOLON {
            $$ = $3;
        }
    |   Type VarDefList SEMICOLON {
            $$ = $2;
        }
    ;
// 常量表达式
ConstExp
    :   AddExp {
            $$ = $1;
        }
    ;
// 常量定义列表
ConstDefList
    :   ConstDefList COMMA ConstDef {
            DeclStmt* node = dynamic_cast<DeclStmt*>($1);
            node->addNext(dynamic_cast<DefNode*>($3));
            $$ = node;
        }
    |   ConstDef {
            DeclStmt* node = new DeclStmt(true);
            node->addNext(dynamic_cast<DefNode*>($1));
            $$ = node;
        }
    ;

VarDefList
    : VarDef {
        DeclStmt* node = new DeclStmt(true);
        node->addNext(dynamic_cast<DefNode*>($1));
        $$ = node;
    }
    | VarDefList COMMA VarDef {
        DeclStmt* node = dynamic_cast<DeclStmt*>($1);
        node->addNext(dynamic_cast<DefNode*>($3));
        $$ = node;
    }
    ;

VarDef
    :  ID {
        if(identifiers->isRedefine($1)) {
            fprintf(stderr, "identifier %s redefine\n", $1);
            exit(EXIT_FAILURE);
        }
        Type* type = TypeSystem::intType;
        SymbolEntry *se = new IdentifierSymbolEntry(type, $1, identifiers->getLevel());
        identifiers->install($1, se);
        $$ = new DefNode(new Id(se), nullptr);
    }
    |  ID ASSIGN Exp {
        if(identifiers->isRedefine($1)) {
            fprintf(stderr, "identifier %s redefine\n", $1);
            exit(EXIT_FAILURE);
        }
        Type* type = TypeSystem::intType;
        SymbolEntry *se = new IdentifierSymbolEntry(type, $1, identifiers->getLevel());
        identifiers->install($1, se);
        $$ = new DefNode(new Id(se), dynamic_cast<Node*>($3));
    }
    // 数组变量的定义
    |   ID ArrConstIndices {
            Type* type = new IntArrayType();
            SymbolEntry *se;
            se = new IdentifierSymbolEntry(type, $1, identifiers->getLevel());
            identifiers->install($1, se);
            Id* id = new Id(se);
            id->addIndices(dynamic_cast<ExprStmtNode*>($2));
            $$ = new DefNode(id, nullptr, false, true);//类型向上转换
        }
    |   ID ArrConstIndices ASSIGN VarInitVal{
            Type* type = new IntArrayType();
            SymbolEntry *se;
            se = new IdentifierSymbolEntry(type, $1, identifiers->getLevel());
            identifiers->install($1, se);
            Id* id = new Id(se);
            id->addIndices(dynamic_cast<ExprStmtNode*>($2));
            $$ = new DefNode(id, dynamic_cast<Node*>($4), false, true);//类型向上转换
        }
    ;
// 常量定义
ConstDef
    :   ID ASSIGN ConstExp {
            // 首先将ID插入符号表中
            Type*  type = TypeSystem::constIntType;
            
            SymbolEntry *se;
            se = new IdentifierSymbolEntry(type, $1, identifiers->getLevel());
            identifiers->install($1, se);
            // 类型向上转换
            $$ = new DefNode(new Id(se), dynamic_cast<Node*>($3), true, false);
        }
    // 数组常量的定义
    |   ID ArrConstIndices ASSIGN ConstInitVal{
            // 首先将ID插入符号表中
            Type* type = new ConstIntArrayType();
            
            SymbolEntry *se;
            se = new IdentifierSymbolEntry(type, $1, identifiers->getLevel());
            identifiers->install($1, se);
            Id* id = new Id(se);
            id->addIndices(dynamic_cast<ExprStmtNode*>($2));
            // 类型向上转换
            $$ = new DefNode(id, dynamic_cast<Node*>($4), true, true);
        }
    ;
    
IOStmt
    : SCAN LP ID RP SEMICOLON {
        SymbolEntry *se = identifiers->lookup($3);
        if(se == nullptr)
        {
            fprintf(stderr, "identifier \"%s\" is undefined\n", (char*)$3);
            delete [](char*)$3;
            assert(se != nullptr);
        }
        $$ = new IOStmt(IOStmt::SCAN, new Id(se));
        delete []$3;
    }
    | PRINT LP Exp RP SEMICOLON {
        $$ = new IOStmt(IOStmt::PRINT, $3);
    }

ReturnStmt
    : RETURN SEMICOLON {
        $$ = new ReturnStmt(nullptr);
    }
    | RETURN Exp SEMICOLON {
        $$ = new ReturnStmt($2);
    }
    ;
    
Exp
    : AddExp {$$ = $1;}
    ;

UnaryExp
    : ADD UnaryExp {$$ = $2;}
    | SUB UnaryExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::SUB, $2);
    }
    | NOT UnaryExp {
        SymbolEntry *tmp = new TemporarySymbolEntry(TypeSystem::boolType, SymbolTable::getLabel());
        $$ = new BinaryExpr(tmp, BinaryExpr::NOT, $2);
    }
    | PrimaryExp {
        $$ =$1;
    }
    ;

PrimaryExp
    : LVal {
        $$ = $1;
    }
    | LP Exp RP  {
        $$ = $2;
    }
    | INTEGER {
        SymbolEntry *se = new ConstantSymbolEntry(TypeSystem::intType, $1);
        $$ = new Constant(se);
    }
    ;

LVal
    : ID {
        SymbolEntry *se = identifiers->lookup($1);
        if(se == nullptr)
        {
            fprintf(stderr, "identifier \"%s\" is undefined\n", (char*)$1);//此处已检查未定义问题
            delete [](char*)$1;
            assert(se != nullptr);
        }
        $$ = new Id(se);
        delete []$1;
    }
    // 数组左值
    |   ID ArrValIndices {
            SymbolEntry *se;
            se = identifiers->lookup($1);
            if(se == nullptr)
            {
                fprintf(stderr, "identifier \"%s\" is undefined\n", (char*)$1);
                delete [](char*)$1;
                assert(se != nullptr);
            }
            Id* newId = new Id(se);
            newId->addIndices(dynamic_cast<ExprStmtNode*>($2));
            $$ =  newId;
            delete []$1;
        }
    ;
    ;

AddExp
    : MulExp {
        $$ = $1;
    }
    | AddExp ADD MulExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        
        $$ = new BinaryExpr(se, BinaryExpr::ADD, $1, $3);
    }
    | AddExp SUB MulExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::SUB, $1, $3);
    }
    ;

MulExp
    : UnaryExp {$$ = $1;}
    | MulExp MUL UnaryExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::MUL, $1, $3);
    }
    | MulExp DIV UnaryExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::DIV, $1, $3);
    }
    | MulExp MOD UnaryExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::MOD, $1, $3);
    }
    ; 

Cond
    : LOrExp {$$ = $1;}
    ;


LAndExp
    : RelExp {$$ = $1;}
    | LAndExp AND RelExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::AND, $1, $3);
    }

    ;
LOrExp
    : LAndExp {$$ = $1;}
    | LOrExp OR LAndExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::OR, $1, $3);
    }

RelExp
    : AddExp {$$ = $1;}
    | RelExp LESS AddExp {
        SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
        $$ = new BinaryExpr(se, BinaryExpr::LESS, $1, $3);
    }
    | RelExp GREATER AddExp {
		SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
		$$ = new BinaryExpr(se, BinaryExpr::GREATER, $1, $3);
	}
	| RelExp EQ AddExp {
		SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
		$$ = new BinaryExpr(se, BinaryExpr::EQ, $1, $3);
	}
	| RelExp NEQ AddExp {
		SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
		$$ = new BinaryExpr(se, BinaryExpr::NEQ, $1, $3);
	}
	| RelExp GEQ AddExp {
		SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
		$$ = new BinaryExpr(se, BinaryExpr::GEQ, $1, $3);
	}
	| RelExp LEQ AddExp {
		SymbolEntry *se = new TemporarySymbolEntry(TypeSystem::intType, SymbolTable::getLabel());
		$$ = new BinaryExpr(se, BinaryExpr::LEQ, $1, $3);
	}
    ;

Type
    : INT {
        $$ = TypeSystem::intType;
    }
    | VOID {
        $$ = TypeSystem::voidType;
    }
    ;
// 数组的常量下标表示
ArrConstIndices 
    :   ArrConstIndices LBRACKET ConstExp RBRACKET {
            ExprStmtNode* node = dynamic_cast<ExprStmtNode*>($1);
            node->addNext($3);
            $$ = node;          
        }
    |   LBRACKET ConstExp RBRACKET {
            ExprStmtNode* node = new ExprStmtNode();
            node->addNext($2);
            $$ = node;
        }
    ;
// 数组的变量下标表示
ArrValIndices 
    :   ArrValIndices LBRACKET Exp RBRACKET {
            ExprStmtNode* node = dynamic_cast<ExprStmtNode*>($1);
            node->addNext($3);
            $$ = node;          
        }
    |   LBRACKET Exp RBRACKET {
            ExprStmtNode* node = new ExprStmtNode();
            node->addNext($2);
            $$ = node;
        }
    ;

// 变量初始化值
VarInitVal
    :   Exp {
            InitValNode* node = new InitValNode(false);
            node->setLeafNode(dynamic_cast<ExprNode*>($1));
            $$ = node;
        }
    // 数组变量的初始化值
    |   LB VarInitValList RB{
            $$ = $2;
        }
    |   LB RB{
            $$ = new InitValNode(false);
    }
    ; 

// 数组变量初始化列表
VarInitValList
    :   VarInitValList COMMA VarInitVal{
            InitValNode* node = dynamic_cast<InitValNode*>($1);
            node->addNext(dynamic_cast<InitValNode*>($3));
            $$ = node;
        }
    |   VarInitVal{
            InitValNode* newNode = new InitValNode(false);
            newNode->addNext(dynamic_cast<InitValNode*>($1));
            $$ = newNode;
        }
    ;

// 常量初始化值
ConstInitVal
    :   ConstExp {
            // 不能直接赋值，否则根本无法判断是list还是expr
            InitValNode* newNode = new InitValNode(true);
            newNode->setLeafNode(dynamic_cast<ExprNode*>($1));
            $$ = newNode;
        }
    // 常量数组的初始化值 
    |   LB ConstInitValList RB{
            $$ = $2;
        }
    |   LB RB{
            $$ = new InitValNode(true);
    }
    ;

// 数组常量初始化列表
ConstInitValList
    :   ConstInitValList COMMA ConstInitVal{
            InitValNode* node = dynamic_cast<InitValNode*>($1);
            node->addNext(dynamic_cast<InitValNode*>($3));
            $$ = node;
        }
    |   ConstInitVal{
            InitValNode* newNode = new InitValNode(true);
            newNode->addNext(dynamic_cast<InitValNode*>($1));
            $$ = newNode;
        }
    ;

%%

int yyerror(char const* message)
{
    std::cerr<<message<<std::endl;
    return -1;
}