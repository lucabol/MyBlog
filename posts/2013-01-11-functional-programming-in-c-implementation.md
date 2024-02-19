---
id: 1120
title: 'Functional programming in C: Implementation'
date: 2013-01-11T16:37:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=135
categories:
  - C
  - Functional
tags:
  - C
  - functional
---
## Cleanup
Let's start simple with the cleanup function. First we need the usual barrage of includes. `G_BEGIN_DECLS` allows the header to be linked in C++.
~~~c
#ifndef L_UTILS_INCLUDED
#define L_UTILS_INCLUDED

#include "glib.h"

G_BEGIN_DECLS

#include <stdlib.h>
#include <stdio.h>
This feature is GCC specific. It uses __attribute((cleanup(f))) where f is the cleanup function. In this case the cleanup function just frees the memory.

#ifdef __GNUC__

 static inline void __autofree(void *p) {
     void **_p = (void**)p;
     free(*_p);
 }
~~~
auto_clean is a building block that you can use to plug in your own cleanup function. In the common case of memory allocation, I created a wrapper macro auto_free to make it even easier.
~~~c
#define auto_clean(f)   __attribute((cleanup(f)))
#define auto_free       auto_clean(__autofree)
~~~
## Lambdas
I took this one from here.

If you think about it, a lambda is just an expression that returns a function. This macro creates a nested function, called fn, inside a statement expression and returns it. Unfortunately these features are gcc specific.

Remember that lambdas are not allocated on the heap, so you have to be careful on how you used them.
~~~c
#define lambda(return_type, function_body)                                          
  ({                                                                                
    return_type __fn__ function_body                                                
    __fn__;                                                                         
  })

#endif
~~~
## Unions
A union type is what you would expect: a struct that contains an unnamed union and a field to specify which type it is. We need the list of types in union_decl to create the kind enum. The usage of __VA_ARGS__ allows to use whatever syntax you want to go into the enum (i.e. specify int values).

Having to specify the the types here is unfortunate as you are going to need to specify it in the union_case macros as well.

I haven't found another way to do it. If you do, let me know.
~~~c
#define union_decl(alg, ...)                                                        
typedef struct alg {                                                                
    enum {  __VA_ARGS__ } kind;                                                     
    union {
~~~
You specify each type for the union with union_type. That looks pretty good to me.
~~~c
#define union_type(type, ...)                                                       
    struct type { __VA_ARGS__ } type;
~~~
Ideally you shouldn't need to specify alg here. Perhaps there is a way to avoid doing so.
~~~c
#define union_end(alg)                                                              
    };} alg;
~~~
You can then set the fields on the union type by using the below macro. Notice the usage of the new struct constructor here to allow optional named parameters.

This is a statement, so it cannot go into an expression place. I think I could make it an expression that returns the existing (or a new) union. This is going to be a sceanrio if people are not using gcc statement expressions.
~~~c
#define union_set(instance, type, ...)                                              
    G_STMT_START {                                                                  
        (instance)->kind     = (type);                                              
        (instance)->type   = (struct type) { __VA_ARGS__ };                         
    } G_STMT_END
~~~
This is an utility macro. It is a version of g_assert that you can use in an expression position.
~~~c
#define g_assert_e(expr) (                                                          
    (G_LIKELY (!expr) ?                                                             
   (void)g_assertion_message_expr (G_LOG_DOMAIN, __FILE__, __LINE__, G_STRFUNC, 
                                             #expr)                             
    : (void) 1) )
~~~
And this allows to fill the default case in a match statement implemented as a ternary operator. It prints out a text representation of the expression and returns it.
~~~c
#define union_fail(...) (g_assert_e(((void)(__VA_ARGS__) , false)), (__VA_ARGS__))
~~~
The rest of the code is commented out. It is a macro way to do pattern matching. For me, the ternary operator is simpler, but I left it there in case you want to play with it.
~~~c
/*
#define union_case_only_s(instance, type, ...)                                      
        G_STMT_START {                                                              
        if((instance)->kind == (type)) {                                            
            G_GNUC_UNUSED struct type* it = &((instance)->type); __VA_ARGS__; }     
        else g_assert_not_reached();                                                
        } G_STMT_END

#define union_case_first_s(alg, instance, type, ...)                                
    G_STMT_START {                                                                  
        alg* private_tmp = (instance);                                              
        if(private_tmp->kind == type) {                                             
            G_GNUC_UNUSED struct type* it = &((private_tmp)->type); __VA_ARGS__; }

#define union_case_s(type, ...)                                                     
        else if(private_tmp->kind == type) {                                        
            G_GNUC_UNUSED struct type* it = &((private_tmp)->type); __VA_ARGS__; }

#define union_case_last_s(type, ...)                                                
        else if(private_tmp->kind == type) {                                        
            G_GNUC_UNUSED struct type* it = &((private_tmp)->type); __VA_ARGS__; }  
            else g_assert_not_reached(); } G_STMT_END

#define union_case_default_s(...)                                                   
        else __VA_ARGS__; } G_STMT_END

// Need to use assert here because g_assert* cannot be used in expressions as it expands to do .. while(0)
#define union_case_only(instance, type, ...)                                        
        ( (instance)->kind == (type) ? (__VA_ARGS__) : (assert(false), __VA_ARGS__) )

#define union_case_first(instance, type, ...)                                       
        ( (instance)->kind == (type) ? (__VA_ARGS__) :

#define union_case(instance, type, ...)                                             
        (instance)->kind == (type) ? (__VA_ARGS__) :

#define union_case_last(instance, type, ...)                                        
        (instance)->kind == (type) ? (__VA_ARGS__) : (assert(false), (__VA_ARGS__)) )
#define union_case_default(...)                                                     
        (__VA_ARGS__) )

*/

G_BEGIN_DECLS

#endif // L_UTILS_INCLUDED
~~~
