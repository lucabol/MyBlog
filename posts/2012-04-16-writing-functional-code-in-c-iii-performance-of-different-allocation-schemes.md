---
id: 89
title: Writing functional code in C++ III – Performance of different allocation schemes
date: 2012-04-16T09:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=89
categories:
  - C
tags:
  - C++
  - functional
---
In this post we are going to look at the performance characteristics of different ways to allocate objects in C++. The goal is to understand what is the best way to allocate objects in a functional style. Code for this post is [here](https://github.com/lucabol/FunctionalCpp/blob/master/allocation_perf.cpp).

First of all, let's define what we are going to allocate:

```cpp
struct Record {
    int Id;
    int Value1;
    int Value2;
    int Value3;
    int Value4;
    int Value5;
    int Value6;
    int Value7;
    int Value8;
    int Value9;
};
```

And a function to initialize it:

```cpp
void record_init(Record& r, int i) {
    r.Id = i;
    r.Value1 = i;
    r.Value2 = i;
    r.Value3 = i;
    r.Value4 = i;
    r.Value5 = i;
    r.Value6 = i;
    r.Value7 = i;
    r.Value8 = i;
    r.Value9 = i;
}
```

And a function to convert it to an int (so that the compiler doesn't optimize away our code):

```cpp
struct to_int {
    typedef int result_type;
    int operator() (const Record& r) const { return r.Id;}
};
```

Let's also define some constants:

```cpp
const int repetitions = 1000;
const int bigBlock = 1000;
```

And a timer class to measure performance:

```cpp
typedef boost::chrono::process_cpu_clock the_clock;
struct timer {
    timer() : start(the_clock::now()) {}
    ~timer() {
        auto stop = the_clock::now();
        auto diff = stop - start;
        std::cout << diff << std::endl;
    }
    the_clock::time_point start;
};
```

Now let's look at different ways to allocate objects. First the normal way:

```cpp
int normal() {
    vector<Record> v;
    for(int i = 0; i < repetitions; ++i) {
        v.clear();
        for(int j = 0; j < bigBlock; ++j) {
            Record r;
            record_init(r, j);
            v.push_back(r);
        }
    }
    return boost::accumulate(v, 0, [](int i, const Record& r) { return i + r.Id;});
}
```

Then using a pod_vector (a vector that doesn't initialize its elements):

```cpp
int podVector() {
    pod_vector<Record, size> v;
    for(int i = 0; i < repetitions; ++i) {
        v.clear();
        for(int j = 0; j < bigBlock; ++j) {
            Record r;
            record_init(r, j);
            v.push_back(r);
        }
    }
    return boost::accumulate(v, 0, [](int i, const Record& r) { return i + r.Id;});
}
```

Then using boost pool allocator:

```cpp
int boostallocator(WhichOne which) {
    boost::pool<> p(sizeof(Record));
    vector<Record, boost::pool_allocator<Record>> v;
    for(int i = 0; i < repetitions; ++i) {
        v.clear();
        for(int j = 0; j < bigBlock; ++j) {
            Record r;
            record_init(r, j);
            v.push_back(r);
        }
    }
    return boost::accumulate(v, 0, [](int i, const Record& r) { return i + r.Id;});
}
```

Then using shared pointers:

```cpp
int pointers(WhichOne which) {
    vector<shared_ptr<Record>> v;
    for(int i = 0; i < repetitions; ++i) {
        v.clear();
        for(int j = 0; j < bigBlock; ++j) {
            auto r = make_shared<Record>();
            record_init(*r, j);
            v.push_back(r);
        }
    }
    return boost::accumulate(v, 0, [](int i, const shared_ptr<Record>& r) { return i + r->Id;});
}
```

Then using Loki smart pointers:

```cpp
typedef Loki::SmartPtr<Record,
                 Loki::RefCounted,
                 Loki::DisallowConversion,
                 Loki::AssertCheck,
                 Loki::DefaultSPStorage> RecordPtr;
```

```cpp
int lokipointers(WhichOne) {
    vector<RecordPtr> v;
    for(int i = 0; i < repetitions; ++i) {
        v.clear();
        for(int j = 0; j < bigBlock; ++j) {
            auto r = RecordPtr(new Record());
            record_init(*r, j);
            v.push_back(r);
        }
    }
    return boost::accumulate(v, 0, [](int i, const RecordPtr& r) { return i + r->Id;});
}
```

The results are quite interesting. The pod_vector is the fastest, followed by the normal vector, followed by the boost pool allocator, followed by the shared pointers, followed by the Loki pointers.

The pod_vector is faster than the normal vector because it doesn't initialize its elements. The normal vector is faster than the boost pool allocator because the boost pool allocator has to maintain a pool of memory. The shared pointers are slower than the boost pool allocator because they have to maintain reference counts. The Loki pointers are slower than the shared pointers because they have to maintain reference counts and they have to check for null pointers.

The conclusion is that if you want to write functional code in C++, you should use pod_vector or normal vector. If you need to share objects between different parts of your code, you should use shared pointers. If you need to share objects between different parts of your code and you need to check for null pointers, you should use Loki pointers.
