use super::*;
use nativeweave_data_contracts::{Codec, wire::hex};
use sha2::{Digest, Sha256};
fn field(id: u16, ty: u16, value: Vec<u8>) -> (u16, u16, Vec<u8>) {
    (id, ty, value)
}
fn u32field(id: u16, value: u32) -> (u16, u16, Vec<u8>) {
    field(id, 1, value.to_le_bytes().to_vec())
}
fn token(id: u16, value: u64) -> (u16, u16, Vec<u8>) {
    field(id, 2, value.to_le_bytes().to_vec())
}
fn control(kind: u16, fields: Vec<(u16, u16, Vec<u8>)>) -> Vec<u8> {
    let start = 16 + fields.len() * 16;
    let size = start + fields.iter().map(|(_, _, v)| v.len()).sum::<usize>();
    let mut bytes = vec![0; size];
    bytes[..2].copy_from_slice(&1u16.to_le_bytes());
    bytes[2..4].copy_from_slice(&kind.to_le_bytes());
    bytes[4..8].copy_from_slice(&(size as u32).to_le_bytes());
    bytes[8..12].copy_from_slice(&(fields.len() as u32).to_le_bytes());
    let mut offset = start;
    for (index, (id, ty, value)) in fields.into_iter().enumerate() {
        let at = 16 + index * 16;
        bytes[at..at + 2].copy_from_slice(&id.to_le_bytes());
        bytes[at + 2..at + 4].copy_from_slice(&ty.to_le_bytes());
        bytes[at + 4..at + 8].copy_from_slice(&(value.len() as u32).to_le_bytes());
        bytes[at + 8..at + 16].copy_from_slice(&(offset as u64).to_le_bytes());
        bytes[offset..offset + value.len()].copy_from_slice(&value);
        offset += value.len();
    }
    bytes
}
fn fixture(file: &str) -> Vec<u8> {
    std::fs::read(
        std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../golden")
            .join(file),
    )
    .unwrap()
}
struct Context {
    root: ModelBinding,
    child: ModelBinding,
    registry: Arc<ParameterRegistry>,
}
impl Context {
    fn new(profile: Profile) -> Self {
        let source = SourceIdentity {
            engine: 9,
            source: 1,
            generation: 1,
            profile,
        };
        let codecs = Arc::new(CodecBindings::new(profile, &[]).unwrap());
        Self {
            root: ModelBinding::new(
                source,
                Arc::new(Model::parse(&fixture("parent-model.json"), profile).unwrap()),
                Arc::clone(&codecs),
            )
            .unwrap(),
            child: ModelBinding::new(
                source,
                Arc::new(Model::parse(&fixture("child-model.json"), profile).unwrap()),
                codecs,
            )
            .unwrap(),
            registry: Arc::new(ParameterRegistry::new(source, 4096).unwrap()),
        }
    }
    fn query(&self) -> QueryArena {
        self.limited(Limits::default())
    }
    fn limited(&self, limits: Limits) -> QueryArena {
        QueryArena::new(
            self.root.clone(),
            Arc::clone(&self.registry),
            self.root.model.table_id(),
            limits,
            full_caps(self.root.source.profile),
            1_000_000,
        )
        .unwrap()
    }
    fn column(&self, name: &str) -> u32 {
        self.root
            .model
            .columns()
            .iter()
            .find(|c| c.name == name)
            .unwrap()
            .id
    }
    fn select(&self, q: &mut QueryArena) {
        let a = q.column(0, self.column("Id")).unwrap();
        let b = q.column(0, self.column("Name")).unwrap();
        let tokens = [a, b].into_iter().flat_map(u64::to_le_bytes).collect();
        q.clause(
            6,
            &control(
                6,
                vec![
                    field(1, 8, tokens),
                    field(2, 5, fixture("parent-projection.bin")),
                ],
            ),
        )
        .unwrap();
    }
}
fn expect<T>(result: Result<T>, status: u32) {
    assert_eq!(result.err().unwrap().status, status);
}
#[test]
fn both_side_operation_goldens_and_projection_hashes() {
    assert_eq!(
        control(6, vec![token(1, 0x100000001)]),
        fixture("where.bin")
    );
    assert_eq!(
        control(
            6,
            vec![
                token(1, 0x100000001),
                u32field(2, 0),
                u32field(3, 1),
                u32field(4, 1)
            ]
        ),
        fixture("order.bin")
    );
    assert_eq!(
        control(6, vec![token(1, 20), token(2, 3)]),
        fixture("limit.bin")
    );
    let c = Context::new(Profile::Sqlite);
    let p = projection_record(
        &fixture("parent-projection.bin"),
        c.root.source,
        1,
        Arc::clone(&c.root.codecs),
        None,
    )
    .unwrap();
    assert_eq!(p.projection.fields().len(), 2);
    assert_eq!(
        hex(&Sha256::digest(p.projection.bytes())),
        hex(&p.projection.hash())
    );
}
#[test]
fn expression_opcode_domains_types_and_nullable_rules() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.query();
    let integer = q.column(0, c.column("Id")).unwrap();
    let text = q.column(0, c.column("Name")).unwrap();
    for op in 1..=10 {
        let result = q.binary(op, integer, integer).unwrap();
        assert_eq!(
            q.expression_type(result).unwrap().codec.id,
            if op <= 6 { 4 } else { 3 }
        );
    }
    let predicate = q.binary(1, integer, integer).unwrap();
    for op in [11, 12] {
        q.binary(op, predicate, predicate).unwrap();
        expect(q.binary(op, integer, integer), 3);
    }
    for op in [13, 14] {
        q.binary(op, integer, integer).unwrap();
    }
    expect(q.binary(1, integer, text), 3);
    expect(q.binary(15, integer, integer), 6);
    expect(q.unary(3, integer), 3);
    expect(q.unary(9, integer), 6);
    let lifted = q.unary(4, integer).unwrap();
    assert!(q.expression_type(lifted).unwrap().codec.nullable);
    expect(q.unary(4, lifted), 3);
    for op in [1, 2] {
        let result = q.unary(op, lifted).unwrap();
        assert!(!q.expression_type(result).unwrap().codec.nullable);
    }
    let one = fixture("value.bin");
    q.value(&one).unwrap();
    q.list(1, integer, &one).unwrap();
    expect(q.list(3, integer, &one), 3);
    let expected = Expectation {
        kind: 3,
        profile: Profile::Sqlite,
        hash: [0; 32],
        entity_id: 0,
        projection_id: 0,
        descriptors: vec![Descriptor {
            id: 1,
            codec: Codec {
                id: 3,
                configuration: None,
                nullable: false,
            },
            bound_codec: 3,
        }],
        exact_rows: Some(0),
    };
    let empty = Batch::encode(&expected, 0, &[]).unwrap();
    let result = q.list(2, integer, &empty).unwrap();
    assert!(!q.expression_type(result).unwrap().codec.nullable);
}
#[test]
fn join_slot_generation_and_transitive_capture_invalidation() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.query();
    let model = q.import_model(c.child.clone()).unwrap();
    let left = q.column(0, c.column("Id")).unwrap();
    let child = c
        .child
        .model
        .columns()
        .iter()
        .find(|c| c.name == "Id")
        .unwrap()
        .id;
    for abort in [false, true] {
        let alias = q
            .clause(
                18,
                &control(
                    6,
                    vec![
                        token(1, model),
                        u32field(2, c.child.model.table_id()),
                        field(
                            3,
                            4,
                            if abort {
                                b"abort".to_vec()
                            } else {
                                b"joined".to_vec()
                            },
                        ),
                        u32field(4, 1),
                    ],
                ),
            )
            .unwrap();
        let right = q.column(alias, child).unwrap();
        assert!(!q.expression_type(right).unwrap().codec.nullable);
        let on = q.binary(1, left, right).unwrap();
        let capture = q.unary(2, right).unwrap();
        expect(q.clause(8, &control(6, vec![])), 4);
        if abort {
            q.clause(19, &control(6, vec![token(1, alias)])).unwrap();
            expect(q.column(alias, child), 3);
        } else {
            assert_eq!(
                q.clause(7, &control(6, vec![token(1, alias), token(2, on)]))
                    .unwrap(),
                alias
            );
            let fresh = q.column(alias, child).unwrap();
            assert!(q.expression_type(fresh).unwrap().codec.nullable);
            q.clause(20, &control(6, vec![token(1, alias)])).unwrap();
        }
        expect(q.expression_type(right), 3);
        expect(q.expression_type(on), 3);
        expect(q.expression_type(capture), 3);
    }
}
#[test]
fn rejected_calls_are_atomic_and_control_ranges_are_checked() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.query();
    let column = q.column(0, c.column("Id")).unwrap();
    let predicate = q.binary(1, column, column).unwrap();
    let valid = control(6, vec![token(1, predicate)]);
    let before = q.counts();
    for index in [0usize, 2, 4, 8, 12, 16, 18, 20, 24] {
        let mut bad = valid.clone();
        bad[index] ^= 0x80;
        assert!(q.clause(1, &bad).is_err());
        assert_eq!(q.counts(), before);
    }
    for length in 0..valid.len() {
        assert!(q.clause(1, &valid[..length]).is_err());
        assert_eq!(q.counts(), before);
    }
    expect(q.clause(23, &valid), 6);
    expect(q.clause(5, &control(6, vec![token(1, u64::MAX)])), 3);
    assert_eq!(q.counts(), before);
}
#[test]
fn budgets_bound_nodes_depth_bytes_and_abort_remains_available() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.limited(Limits {
        nodes: 4,
        depth: 2,
        ..Limits::default()
    });
    let a = q.column(0, c.column("Id")).unwrap();
    let b = q.unary(1, a).unwrap();
    expect(q.unary(3, b), 13);
    let before = q.counts();
    let large = vec![0; 4 * 1024 * 1024 + 1];
    expect(q.value(&large), 3);
    assert_eq!(q.counts(), before);
    let mut q = c.limited(Limits {
        nodes: 2,
        ..Limits::default()
    });
    let model = q.import_model(c.child.clone()).unwrap();
    let alias = q
        .clause(
            18,
            &control(
                6,
                vec![
                    token(1, model),
                    u32field(2, c.child.model.table_id()),
                    field(3, 4, b"r".to_vec()),
                    u32field(4, 1),
                ],
            ),
        )
        .unwrap();
    q.clause(19, &control(6, vec![token(1, alias)])).unwrap();
    assert_eq!(q.counts().0, 2);
    expect(q.column(0, c.column("Id")), 13);
}
#[test]
fn aggregate_widening_and_exact_over_root_tags() {
    let c = Context::new(Profile::PostgreSql);
    let mut q = c.query();
    let input = q.column(0, c.column("Id")).unwrap();
    let aggregate = |fun, result| {
        control(
            6,
            vec![
                u32field(1, fun),
                token(2, input),
                u32field(3, 0),
                u32field(5, result),
            ],
        )
    };
    expect(q.clause(13, &aggregate(2, 12)), 3);
    expect(q.clause(13, &aggregate(3, 1)), 3);
    let sum = q.clause(13, &aggregate(2, 3)).unwrap();
    assert!(q.expression_type(sum).unwrap().codec.nullable);
    q.clause(13, &aggregate(3, 11)).unwrap();
    let count = q.clause(13, &aggregate(1, 3)).unwrap();
    assert!(!q.expression_type(count).unwrap().codec.nullable);
    let window = q.clause(11, &control(6, vec![u32field(1, 0)])).unwrap();
    let over = q
        .clause(21, &control(6, vec![token(1, sum), token(2, window)]))
        .unwrap();
    expect(
        q.clause(21, &control(6, vec![token(1, over), token(2, window)])),
        3,
    );
    let combined = q.binary(7, sum, sum).unwrap();
    expect(
        q.clause(21, &control(6, vec![token(1, combined), token(2, window)])),
        3,
    );
    let predicate = q.list(1, sum, &fixture("value.bin")).err();
    assert!(predicate.is_some()); // SQLite wire profile must not cross PG.
    let mut s = c.query();
    let input = s.column(0, c.column("Id")).unwrap();
    let sum = s
        .clause(
            13,
            &control(
                6,
                vec![
                    u32field(1, 2),
                    token(2, input),
                    u32field(3, 0),
                    u32field(5, 3),
                ],
            ),
        )
        .unwrap();
    let predicate = s.binary(1, sum, sum).unwrap();
    expect(s.clause(1, &control(6, vec![token(1, predicate)])), 3);
}
#[test]
fn window_frame_capability_lock_and_text_failures() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.query();
    let input = q.column(0, c.column("Name")).unwrap();
    let window = q.clause(11, &control(6, vec![u32field(1, 0)])).unwrap();
    q.clause(
        11,
        &control(6, vec![u32field(1, 1), token(2, window), token(3, input)]),
    )
    .unwrap();
    q.clause(
        11,
        &control(
            6,
            vec![
                u32field(1, 2),
                token(2, window),
                token(3, input),
                u32field(4, 0),
                u32field(5, 1),
            ],
        ),
    )
    .unwrap();
    q.clause(
        11,
        &control(
            6,
            vec![
                u32field(1, 3),
                token(2, window),
                u32field(6, 0),
                u32field(7, 2),
            ],
        ),
    )
    .unwrap();
    expect(
        q.clause(
            11,
            &control(
                6,
                vec![
                    u32field(1, 3),
                    token(2, window),
                    u32field(6, 2),
                    u32field(7, 0),
                ],
            ),
        ),
        3,
    );
    expect(
        q.clause(12, &control(6, vec![u32field(1, 0), u32field(2, 0)])),
        6,
    );
    expect(
        q.clause(
            16,
            &control(
                6,
                vec![
                    u32field(1, 4),
                    token(2, input),
                    field(3, 4, b"not_allowed".to_vec()),
                    u32field(4, 92),
                ],
            ),
        ),
        6,
    );
    let mut caps = full_caps(Profile::Sqlite);
    caps.windows = false;
    let mut unsupported = QueryArena::new(
        c.root.clone(),
        Arc::clone(&c.registry),
        c.root.model.table_id(),
        Limits::default(),
        caps,
        1,
    )
    .unwrap();
    expect(unsupported.clause(11, &control(6, vec![u32field(1, 0)])), 6);
}
#[test]
fn clone_import_keeps_source_mutable_and_transitive_budgets_finite() {
    let c = Context::new(Profile::Sqlite);
    let q = c.query();
    let clone = q.clone_selected().unwrap();
    assert_eq!(clone.state(), QueryState::Mutable);
    let mut source = c.query();
    c.select(&mut source);
    let mut clone = source.clone_selected().unwrap();
    let plan = clone.seal(8).unwrap();
    source.column(0, c.column("Id")).unwrap();
    let mut small = c.limited(Limits {
        nodes: plan.nodes,
        ..Limits::default()
    });
    expect(small.import_plan(Arc::clone(&plan)), 13);
    assert_eq!(small.counts(), (0, 0));
    let mut chain = plan;
    for _ in 0..3 {
        let mut q = c.query();
        c.select(&mut q);
        q.import_plan(chain).unwrap();
        chain = q.seal(8).unwrap();
    }
    assert!(chain.depth >= 4);
    let mut shallow = c.limited(Limits {
        depth: 2,
        ..Limits::default()
    });
    expect(shallow.import_plan(chain), 13);
}
#[test]
fn parameter_source_identity_schema_union_and_execute_copy() {
    let c = Context::new(Profile::Sqlite);
    let identity = ParameterIdentity {
        id: 9,
        name: "p".into(),
        codec: Codec {
            id: 3,
            configuration: None,
            nullable: false,
        },
        bound_codec: 3,
    };
    let mut a = c.query();
    a.parameter(identity.clone()).unwrap();
    let mut b = c.query();
    let mut wrong_id = identity.clone();
    wrong_id.name = "wrong".into();
    expect(b.parameter(wrong_id), 3);
    let mut duplicate = identity.clone();
    duplicate.id = 10;
    b.parameter(duplicate).unwrap();
    c.select(&mut b);
    let p = b.seal(8).unwrap();
    let before = a.counts();
    expect(a.import_plan(p), 3);
    assert_eq!(a.counts(), before);
    c.select(&mut a);
    let plan = a.seal(0).unwrap();
    let encoded = Batch::encode(
        &plan.parameter_expectation(),
        1,
        &[Some(&19i64.to_le_bytes())],
    )
    .unwrap();
    let mut borrowed = encoded.clone();
    let args = plan
        .execution_arguments(c.root.source, &borrowed, Limits::default())
        .unwrap();
    borrowed.fill(0);
    assert_eq!(&*args.parameters, encoded);
    let mut wrong = c.root.source;
    wrong.generation = 2;
    expect(
        plan.execution_arguments(wrong, &encoded, Limits::default()),
        4,
    );
    let mut corrupt = encoded.clone();
    corrupt[96] ^= 1;
    expect(
        plan.execution_arguments(c.root.source, &corrupt, Limits::default()),
        3,
    );
}
#[test]
fn independent_relation_cache_copy_projection_and_retained_source_close() {
    let c = Context::new(Profile::Sqlite);
    let mut cache =
        RelationRegistry::new(c.root.source, 1, 4 * 1024 * 1024, relation_caps()).unwrap();
    let relation = cache
        .register(c.root.clone(), c.child.clone(), &fixture("relation.bin"))
        .unwrap();
    let again = cache
        .register(c.root.clone(), c.child.clone(), &fixture("relation.bin"))
        .unwrap();
    assert!(Arc::ptr_eq(&relation, &again));
    let projection = projection_record(
        &fixture("child-projection.bin"),
        c.root.source,
        7,
        Arc::clone(&c.root.codecs),
        None,
    )
    .unwrap();
    let mut key = fixture("key.bin");
    let args = relation
        .load(
            c.root.source,
            &key,
            projection.clone(),
            Limits::default(),
            1,
        )
        .unwrap();
    key.fill(0);
    assert_eq!(&*args.key, fixture("key.bin"));
    cache.close();
    assert_eq!(cache.counts(), (0, 0));
    assert_eq!(args.relation.relation.hash(), relation.relation.hash());
    expect(
        cache.register(c.root.clone(), c.child.clone(), &fixture("relation.bin")),
        4,
    );
    let wrong = projection_record(
        &fixture("parent-projection.bin"),
        c.root.source,
        8,
        Arc::clone(&c.root.codecs),
        None,
    )
    .unwrap();
    expect(
        relation.load(
            c.root.source,
            &fixture("key.bin"),
            wrong,
            Limits::default(),
            1,
        ),
        3,
    );
    let mut corrupt = fixture("key.bin");
    corrupt[102] = 1;
    expect(
        relation.load(c.root.source, &corrupt, projection, Limits::default(), 1),
        3,
    );
}
#[test]
fn state_poison_wrong_generation_and_root_mutation_shape() {
    let c = Context::new(Profile::Sqlite);
    let mut a = c.query();
    let mut b = c.query();
    let foreign_token = a.column(0, c.column("Id")).unwrap();
    expect(b.unary(1, foreign_token), 3);
    expect(b.seal(7), 6);
    a.poison();
    expect(a.column(0, c.column("Id")), 10);
    a.close();
    expect(a.column(0, c.column("Id")), 4);
    let mut q = c.query();
    let col = q.column(0, c.column("Id")).unwrap();
    let predicate = q.binary(1, col, col).unwrap();
    q.clause(1, &control(6, vec![token(1, predicate)])).unwrap();
    let plan = q.seal(7).unwrap();
    expect(q.seal(7), 4);
    let values = Batch::encode(&plan.parameter_expectation(), 1, &[]).unwrap();
    plan.execution_arguments(c.root.source, &values, Limits::default())
        .unwrap();
    assert_eq!(q.state(), QueryState::Submitted);
    expect(
        plan.execution_arguments(c.root.source, &values, Limits::default()),
        4,
    );
}

#[test]
fn remaining_direct_clauses_case_text_cte_subquery_timeout_and_update() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.query();
    let id = q.column(0, c.column("Id")).unwrap();
    let name = q.column(0, c.column("Name")).unwrap();
    let predicate = q.binary(1, id, id).unwrap();
    q.clause(1, &control(6, vec![token(1, predicate)])).unwrap();
    q.clause(2, &control(6, vec![token(1, predicate)])).unwrap();
    q.clause(4, &control(6, vec![token(1, id)])).unwrap();
    q.clause(8, &control(6, vec![])).unwrap();
    let case = q
        .clause(
            15,
            &control(6, vec![token(1, predicate), token(2, id), token(3, id)]),
        )
        .unwrap();
    assert_eq!(q.expression_type(case).unwrap().codec.id, 3);
    let expected = Expectation {
        kind: 3,
        profile: Profile::Sqlite,
        hash: [0; 32],
        entity_id: 0,
        projection_id: 0,
        descriptors: vec![Descriptor {
            id: 1,
            codec: Codec {
                id: 5,
                configuration: None,
                nullable: false,
            },
            bound_codec: 5,
        }],
        exact_rows: Some(1),
    };
    let text = Batch::encode(&expected, 1, &[Some(b"%_\\literal")]).unwrap();
    for op in 0..=3 {
        let result = q
            .clause(
                16,
                &control(
                    6,
                    vec![
                        u32field(1, op),
                        token(2, name),
                        field(3, 6, text.clone()),
                        u32field(4, 92),
                    ],
                ),
            )
            .unwrap();
        assert_eq!(q.expression_type(result).unwrap().codec.id, 4);
    }
    q.clause(
        16,
        &control(
            6,
            vec![
                u32field(1, 4),
                token(2, name),
                field(3, 4, b"BINARY".to_vec()),
                u32field(4, 92),
            ],
        ),
    )
    .unwrap();
    q.clause(
        22,
        &control(6, vec![field(1, 3, 12345u64.to_le_bytes().to_vec())]),
    )
    .unwrap();
    let mut body = c.query();
    c.select(&mut body);
    let cte = CteReference::create(c.root.clone(), c.root.model.table_id(), &body, 0).unwrap();
    let imported = q.import_cte(cte).unwrap();
    q.clause(10, &control(6, vec![token(1, imported)])).unwrap();
    expect(q.clause(10, &control(6, vec![token(1, imported)])), 3);
    let mut clone = body.clone_selected().unwrap();
    let shape = clone.seal(8).unwrap();
    let imported = q.import_plan(shape).unwrap();
    q.clause(14, &control(6, vec![token(1, imported), u32field(2, 0)]))
        .unwrap();
    expect(
        q.clause(
            14,
            &control(6, vec![token(1, imported), u32field(2, 1), token(3, id)]),
        ),
        3,
    );
    c.select(&mut q);
    let plan = q.seal(0).unwrap();
    assert_eq!(plan.timeout_ns, 12345);
    let mut update = c.query();
    let id = update.column(0, c.column("Id")).unwrap();
    let name = update.column(0, c.column("Name")).unwrap();
    let predicate = update.binary(1, id, id).unwrap();
    update
        .clause(1, &control(6, vec![token(1, predicate)]))
        .unwrap();
    update
        .clause(
            17,
            &control(6, vec![u32field(1, c.column("Name")), token(2, name)]),
        )
        .unwrap();
    expect(
        update.clause(
            17,
            &control(6, vec![u32field(1, c.column("Name")), token(2, name)]),
        ),
        3,
    );
    expect(
        update.clause(
            17,
            &control(6, vec![u32field(1, c.column("Id")), token(2, id)]),
        ),
        3,
    );
    update.seal(6).unwrap();
}
#[test]
fn relation_capability_negatives_and_single_submission_retention() {
    let c = Context::new(Profile::Sqlite);
    for missing in 0..5 {
        let mut caps = relation_caps();
        match missing {
            0 => caps.metadata = false,
            1 => caps.scalar_codecs = false,
            2 => caps.query = false,
            3 => caps.streaming = false,
            _ => caps.explicit_relationships = false,
        };
        expect(RelationRegistry::new(c.root.source, 1, 4096, caps), 6);
    }
    let mut ordinary = c.query();
    c.select(&mut ordinary);
    let plan = ordinary.seal(0).unwrap();
    let source = c.root.source;
    let values = Batch::encode(&plan.parameter_expectation(), 1, &[]).unwrap();
    let barrier = Arc::new(std::sync::Barrier::new(3));
    let mut threads = Vec::new();
    for _ in 0..2 {
        let plan = Arc::clone(&plan);
        let barrier = Arc::clone(&barrier);
        let values = values.clone();
        threads.push(std::thread::spawn(move || {
            barrier.wait();
            plan.execution_arguments(source, &values, Limits::default())
                .is_ok()
        }));
    }
    barrier.wait();
    let accepted = threads
        .into_iter()
        .map(|thread| usize::from(thread.join().unwrap()))
        .sum::<usize>();
    assert_eq!(accepted, 1);
    assert_eq!(ordinary.state(), QueryState::Submitted);
    let mut prepared = c.query();
    c.select(&mut prepared);
    let prepared = prepared.seal(8).unwrap();
    let values = Batch::encode(&prepared.parameter_expectation(), 1, &[]).unwrap();
    prepared
        .execution_arguments(source, &values, Limits::default())
        .unwrap();
    prepared
        .execution_arguments(source, &values, Limits::default())
        .unwrap();
    let root = Arc::downgrade(&plan.root.model);
    drop(ordinary);
    drop(c);
    assert!(root.upgrade().is_some());
    assert!(!plan.root.model.bytes().is_empty());
}

#[test]
fn exact_scalar_empty_alias_sentinel_only() {
    let c = Context::new(Profile::Sqlite);
    let canonical=b"{\"version\":1,\"fields\":[{\"ordinal\":0,\"name\":\"\",\"codec\":3,\"codec_config\":null,\"nullable\":false}]}";
    let field_record = control(
        22,
        vec![
            u32field(1, 0),
            field(2, 4, Vec::new()),
            u32field(3, 3),
            u32field(4, 0),
        ],
    );
    let mut sequence = 1u32.to_le_bytes().to_vec();
    sequence.extend_from_slice(&(field_record.len() as u32).to_le_bytes());
    sequence.extend_from_slice(&field_record);
    let record = control(
        13,
        vec![
            field(1, 5, sequence),
            field(2, 5, Sha256::digest(canonical).to_vec()),
        ],
    );
    let projection =
        projection_record(&record, c.root.source, 1, Arc::clone(&c.root.codecs), None).unwrap();
    assert_eq!(projection.projection.bytes(), canonical);
    assert_eq!(projection.projection.fields()[0].name, "");
}

#[test]
fn aggregate_list_with_matching_profile_remains_illegal_in_where() {
    let c = Context::new(Profile::Sqlite);
    let mut q = c.query();
    let column = q.column(0, c.column("Id")).unwrap();
    let sum = q
        .clause(
            13,
            &control(
                6,
                vec![
                    u32field(1, 2),
                    token(2, column),
                    u32field(3, 0),
                    u32field(5, 3),
                ],
            ),
        )
        .unwrap();
    let predicate = q.list(1, sum, &fixture("value.bin")).unwrap();
    assert!(q.expression_type(predicate).unwrap().aggregate);
    expect(q.clause(1, &control(6, vec![token(1, predicate)])), 3);
}

#[test]
fn exact_operation_capability_bits_and_internal_snapshot_exception() {
    let c = Context::new(Profile::Sqlite);
    let create = |caps| {
        QueryArena::new(
            c.root.clone(),
            Arc::clone(&c.registry),
            c.root.model.table_id(),
            Limits::default(),
            caps,
            1,
        )
        .unwrap()
    };
    let mut caps = full_caps(Profile::Sqlite);
    caps.explicit_relationships = false;
    let mut q = create(caps);
    let model = q.import_model(c.child.clone()).unwrap();
    expect(
        q.clause(
            18,
            &control(
                6,
                vec![
                    token(1, model),
                    u32field(2, c.child.model.table_id()),
                    field(3, 4, b"r".to_vec()),
                    u32field(4, 1),
                ],
            ),
        ),
        6,
    );
    let mut caps = full_caps(Profile::Sqlite);
    caps.prepared = false;
    caps.set_operations = false;
    caps.recursive_cte = false;
    let mut q = create(caps);
    c.select(&mut q);
    let mut clone = q.clone_selected().unwrap();
    let shape = clone.seal(8).unwrap();
    let values = Batch::encode(&shape.parameter_expectation(), 1, &[]).unwrap();
    expect(
        shape.execution_arguments(c.root.source, &values, Limits::default()),
        6,
    );
    let imported = q.import_plan(shape).unwrap();
    expect(
        q.clause(9, &control(6, vec![token(1, imported), u32field(2, 0)])),
        6,
    );
    expect(
        CteReference::create(c.root.clone(), c.root.model.table_id(), &q, 1),
        6,
    );
    expect(Capabilities::from_mask(1u64 << 63, Profile::Sqlite), 3);
    for bit in [0, 1, 23] {
        let caps = Capabilities::from_mask(((1 << 25) - 1) & !(1 << bit), Profile::Sqlite).unwrap();
        expect(
            QueryArena::new(
                c.root.clone(),
                Arc::clone(&c.registry),
                c.root.model.table_id(),
                Limits::default(),
                caps,
                1,
            ),
            6,
        );
    }
}

#[test]
fn explicit_zero_timeout_is_retained_for_expiration_before_dispatch() {
    for profile in [Profile::Sqlite, Profile::PostgreSql] {
        let c = Context::new(profile);
        let mut q = c.query();
        q.clause(
            22,
            &control(6, vec![field(1, 3, 0u64.to_le_bytes().to_vec())]),
        )
        .unwrap();
        c.select(&mut q);
        assert_eq!(q.seal(0).unwrap().timeout_ns, 0);
    }
}
